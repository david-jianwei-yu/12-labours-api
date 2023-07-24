import re
import copy
import queue
import threading

from fastapi import HTTPException, status

from app.config import Gen3Config
from app.data_schema import GraphQLQueryItem, GraphQLPaginationItem


class Pagination(object):
    def __init__(self, fg, f, s, sgqlc):
        self.FG = fg
        self.F = f
        self.S = s
        self.SGQLC = sgqlc

    def generate_dictionary(self, data):
        dataset_dict = {}
        for ele in data:
            dataset_id = ele["submitter_id"]
            if dataset_id not in dataset_dict:
                dataset_dict[dataset_id] = ele
        return dataset_dict

    def get_pagination_count(self, data):
        public_result = self.generate_dictionary(data["count_public"])
        private_result = self.generate_dictionary(data["count_private"])
        # Default datasets exist in public repository only,
        # Will contain all available datasets after updating
        display_data = list(public_result.keys())
        # Exist in both public and private repository
        match_pair = []
        # Exist in private repository only
        private_only = []
        for id in private_result.keys():
            if id not in public_result:
                display_data.append(id)
                private_only.append(id)
            else:
                match_pair.append(id)
        data_relation = {
            "match_pair": match_pair,
            "private_only": private_only
        }
        return len(display_data), data_relation

    def threading_fetch(self, items):
        result_queue = queue.Queue()
        threads = []
        for args in items:
            t = threading.Thread(target=self.SGQLC.get_queried_result,
                                 args=(*args, result_queue))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        result = {}
        while not result_queue.empty():
            data = result_queue.get()
            result.update(data)
        return result

    def update_pagination_data(self, item, count, relation, data, is_public_access_filtered):
        match_pair = relation["match_pair"]
        private_only = relation["private_only"]
        display = self.generate_dictionary(data["display_public"])
        item.access.remove(Gen3Config.GEN3_PUBLIC_ACCESS)
        items = []
        if match_pair != []:
            for ele in match_pair:
                if ele in display:
                    query_item = GraphQLQueryItem(node="experiment_query", filter={
                        "submitter_id": [ele]}, access=item.access)
                    items.append((query_item, ele))

        # Add private only datasets when datasets can be displayed in one page
        # or when the last page be displayed when there are multiple pages
        if private_only != []:
            if count <= item.limit or item.limit < count <= item.page*item.limit:
                for ele in private_only:
                    query_item = GraphQLQueryItem(node="experiment_query", filter={
                        "submitter_id": [ele]}, access=item.access)
                items.append((query_item, ele))

        # Query displayed datasets with private access
        private_replace_set = self.threading_fetch(items)
        # Replace the dataset if it has a private version
        # or add the dataset if it is only in private repository
        if not is_public_access_filtered:
            for id in private_replace_set.keys():
                display[id] = private_replace_set[id][0]
        return list(display.values())

    def get_pagination_data(self, item):
        public_access = Gen3Config.GEN3_PUBLIC_ACCESS
        display_public_item = GraphQLPaginationItem(
            limit=item.limit, page=item.page, filter=item.filter, access=[public_access])

        count_public_item = GraphQLPaginationItem(
            node="experiment_pagination_count", filter=item.filter, access=[public_access])

        private_access = copy.deepcopy(item.access)
        private_access.remove(public_access)
        count_private_item = GraphQLPaginationItem(
            node="experiment_pagination_count", filter=item.filter, access=private_access)

        items = [
            (display_public_item, "display_public"),
            (count_public_item, "count_public"),
            (count_private_item, "count_private")
        ]
        return self.threading_fetch(items)

    def handle_pagination_item_filter(self, field, facets, extra_filter):
        FILTERS = self.FG.get_filters()
        value_list = []
        for facet in facets:
            # Use .title() to make it non-case sensitive
            facet_name = facet.title()
            for ele in FILTERS:
                if ele in extra_filter:
                    filter_dict = extra_filter
                else:
                    filter_dict = FILTERS
                # Check if title can match with a exist filter object
                if filter_dict[ele]["field"] == field:
                    # Check if ele_name is a key under filter object element field
                    if facet_name not in filter_dict[ele]["facets"]:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or unauthorized facet passed in")

                    facet_value = filter_dict[ele]["facets"][facet_name]
                    if type(facet_value) == list:
                        value_list.extend(facet_value)
                    else:
                        value_list.append(facet_value)
        return {field: value_list}

    def update_pagination_item(self, item, input):
        is_public_access_filtered = False
        if item.filter != {}:
            FIELDS = self.F.get_fields()
            extra_filter = self.FG.generate_extra_filter(item.access)
            temp_node_dict = {}
            filter_dict = {"submitter_id": []}
            for node_filed, facet_name in item.filter.items():
                filter_node = node_filed.split(">")[0]
                filter_field = node_filed.split(">")[1]
                # Update filter based on authority
                valid_filter = self.handle_pagination_item_filter(
                    filter_field, facet_name, extra_filter)
                query_item = GraphQLQueryItem(
                    node=filter_node, filter=valid_filter)
                if filter_node == "experiment_filter":
                    query_item.access = valid_filter["project_id"]
                    if Gen3Config.GEN3_PUBLIC_ACCESS in query_item.access:
                        is_public_access_filtered = True
                else:
                    query_item.access = item.access

                node_name = re.sub('_filter', '', filter_node)
                # Only do fetch when there is no related temp data stored in temp_node_dict
                # or the node field type is "String"
                if node_name not in temp_node_dict or filter_field not in FIELDS:
                    query_result = self.SGQLC.get_queried_result(query_item)
                    # The data will be stored when the field type is an "Array"
                    # The default filter relation of the Gen3 "Array" type field is "AND"
                    # We need "OR", therefore entire node data will go through a self-written filter function
                    if filter_field in FIELDS:
                        temp_node_dict[node_name] = query_result[node_name]
                elif node_name in temp_node_dict and filter_field in FIELDS:
                    query_result = temp_node_dict
                filter_dict["submitter_id"].append(self.F.get_filtered_datasets(
                    query_item.filter, query_result[node_name]))
            item.filter = filter_dict
            self.F.filter_relation(item)

        if input != "":
            # If input does not match any content in the database, item.search will be empty dictionary
            item.search["submitter_id"] = self.S.get_searched_datasets(input)
            if item.search != {} and ("submitter_id" not in item.filter or item.filter["submitter_id"] != []):
                self.S.search_filter_relation(item)

        if Gen3Config.GEN3_PUBLIC_ACCESS not in item.access:
            item.access.append(Gen3Config.GEN3_PUBLIC_ACCESS)
        return is_public_access_filtered
