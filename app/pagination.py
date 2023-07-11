import re
import copy
import queue
import threading

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

    def get_pagination_count(self, public, private):
        public_result = self.generate_dictionary(public)
        private_result = self.generate_dictionary(private)
        # Default datasets exist in public repository only,
        # Will contain all available datasets after updating
        displayed = list(public_result.keys())
        # Exist in both public and private repository
        match_pair = []
        # Exist in private repository only
        private_only = []
        for id in private_result.keys():
            if id not in public_result:
                displayed.append(id)
                private_only.append(id)
            else:
                match_pair.append(id)
        return len(displayed), match_pair, private_only

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

    def update_pagination_data(self, item, total, match, private, public):
        item.access.remove(Gen3Config.PUBLIC_ACCESS)
        result = self.generate_dictionary(public)
        items = []

        if match != []:
            for ele in match:
                if ele in result:
                    query_item = GraphQLQueryItem(node="experiment_query", filter={
                        "submitter_id": [ele]}, access=item.access)
                    items.append((query_item, ele))

        # Add private only datasets when datasets can be displayed in one page
        # or when the last page be displayed when there are multiple pages
        if private != []:
            if total <= item.limit or item.limit < total <= item.page*item.limit:
                for ele in private:
                    query_item = GraphQLQueryItem(node="experiment_query", filter={
                        "submitter_id": [ele]}, access=item.access)
                items.append((query_item, ele))

        # Query displayed datasets with private access
        private_result = self.threading_fetch(items)
        # Replace the dataset if it has a private version
        # or add the dataset if it is only in private repository
        for id in private_result.keys():
            result[id] = private_result[id][0]
        return list(result.values())

    def get_pagination_data(self, item):
        public_access = Gen3Config.PUBLIC_ACCESS
        public_item = GraphQLPaginationItem(
            limit=item.limit, page=item.page, filter=item.filter, access=[public_access])
        count_public_item = GraphQLPaginationItem(
            node="experiment_pagination_count", filter=item.filter, access=[public_access])
        private_access = copy.deepcopy(item.access)
        private_access.remove(public_access)
        count_private_item = GraphQLPaginationItem(
            node="experiment_pagination_count", filter=item.filter, access=private_access)

        items = [
            (public_item, "public"),
            (count_public_item, "count_public"),
            (count_private_item, "count_private")
        ]
        return self.threading_fetch(items)

    def update_filter_values(self, filter, access):
        FILTERS = self.FG.get_filters()
        extra_filter = self.FG.generate_extra_filter(access)
        field = list(filter.keys())[0]
        value_list = []
        for ele_name in filter[field]:
            # Use .title() to make it non-case sensitive
            name = ele_name.title()
            for ele in FILTERS:
                if ele in extra_filter:
                    filter_dict = extra_filter
                else:
                    filter_dict = FILTERS
                # Check if ele can match with a exist filter object
                if filter_dict[ele]["field"] == field:
                    # Check if ele_name is a key under filter object element field
                    if name in filter_dict[ele]["element"]:
                        ele_value = filter_dict[ele]["element"][name]
                        if type(ele_value) == list:
                            value_list.extend(ele_value)
                        else:
                            value_list.append(ele_value)
                    else:
                        return filter
        return {field: value_list}

    def update_pagination_item(self, item, input):
        FIELDS = self.F.get_fields()
        if item.filter != {}:
            filter_dict = {"submitter_id": []}
            temp_node_dict = {}
            for element in item.filter.values():
                filter_node = element["node"]
                # Update filter based on authority
                filter_field = self.update_filter_values(
                    element["filter"], item.access)
                query_item = GraphQLQueryItem(
                    node=filter_node, filter=filter_field)
                if filter_node == "experiment_filter":
                    query_item.access = filter_field["project_id"]
                else:
                    query_item.access = item.access
                filter_node = re.sub('_filter', '', filter_node)
                filter_field = list(filter_field.keys())[0]
                # Only do fetch when there is no related temp data stored in temp_node_dict
                # or the node field type is "String"
                if filter_node not in temp_node_dict or filter_field not in FIELDS:
                    query_result = self.SGQLC.get_queried_result(query_item)
                    # The data will be stored when the field type is an "Array"
                    # The default filter relation of the Gen3 "Array" type field is "AND"
                    # We need "OR", therefore entire node data will go through a self-written filter function
                    if filter_field in FIELDS:
                        temp_node_dict[filter_node] = query_result[filter_node]
                elif filter_node in temp_node_dict and filter_field in FIELDS:
                    query_result = temp_node_dict
                filter_dict["submitter_id"].append(self.F.get_filtered_datasets(
                    query_item.filter, query_result[filter_node]))
            item.filter = filter_dict
            self.F.filter_relation(item)

        if input != "":
            # If input does not match any content in the database, item.search will be empty dictionary
            item.search["submitter_id"] = self.S.get_searched_datasets(input)
            if item.search != {} and ("submitter_id" not in item.filter or item.filter["submitter_id"] != []):
                self.S.search_filter_relation(item)

        if item.access == []:
            item.access.append(Gen3Config.PUBLIC_ACCESS)
