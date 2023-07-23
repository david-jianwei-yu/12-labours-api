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

    def get_pagination_order(self, item):
        query_item = GraphQLQueryItem(
            node="pagination_order_by_dataset_description", access=item.access, asc=item.asc, desc=item.desc)
        if "asc" in item.order:
            query_item.asc = "title"
        elif "desc" in item.order:
            query_item.desc = "title"
        query_result = self.SGQLC.get_queried_result(query_item)

        # Include both public and private if have the access
        ordered_whole_datasets = []
        for ele in query_result[query_item.node]:
            dataset_id = ele["experiments"][0]["submitter_id"]
            if dataset_id not in ordered_whole_datasets:
                ordered_whole_datasets.append(dataset_id)

        ordered_filtered_datasets = []
        ordered_datasets = []
        if "submitter_id" in item.filter:
            for dataset in ordered_whole_datasets:
                if dataset in item.filter["submitter_id"]:
                    ordered_filtered_datasets.append(dataset)
            ordered_datasets = ordered_filtered_datasets
        else:
            ordered_datasets = ordered_whole_datasets
        return ordered_datasets

    def get_pagination_data(self, item, match_pair, is_public_access_filtered):
        if "title" in item.order.lower():
            # Get an ordered dataset list to update the item.filter
            # item.filter will be updated based on the page and limit passed in
            ordered_datasets = self.get_pagination_order(item)
            start = (item.page-1)*item.limit
            end = item.page*item.limit
            item.filter["submitter_id"] = ordered_datasets[start:end]
            item.page = 1

        query_item = GraphQLPaginationItem(
            limit=item.limit, page=item.page, filter=item.filter, access=item.access, order=item.order, asc=item.asc, desc=item.desc)
        query_result = self.SGQLC.get_queried_result(query_item)
        displayed_datasets = self.generate_dictionary(
            query_result[query_item.node])

        item.access.remove(Gen3Config.GEN3_PUBLIC_ACCESS)
        items = []
        # Query displayed datasets which have private version
        if match_pair != []:
            for dataset in match_pair:
                if dataset in displayed_datasets:
                    query_item = GraphQLQueryItem(node="experiment_query", filter={
                        "submitter_id": [dataset]}, access=item.access)
                    items.append((query_item, dataset))

        private_replacement = self.threading_fetch(items)

        if not is_public_access_filtered:
            # Replace the dataset if it has a private version
            for dataset in private_replacement.keys():
                displayed_datasets[dataset] = private_replacement[dataset][0]
        return list(displayed_datasets.values())

    def get_pagination_count(self, item):
        public_access = Gen3Config.GEN3_PUBLIC_ACCESS
        public_pagination_count_item = GraphQLPaginationItem(
            node="experiment_pagination_count", filter=item.filter, access=[public_access])
        private_access = copy.deepcopy(item.access)
        private_access.remove(public_access)
        private_pagination_count_item = GraphQLPaginationItem(
            node="experiment_pagination_count", filter=item.filter, access=private_access)

        fetched_data = self.threading_fetch([
            (public_pagination_count_item, "public_pagination"),
            (private_pagination_count_item, "private_pagination")
        ])

        public_result = self.generate_dictionary(
            fetched_data["public_pagination"])
        private_result = self.generate_dictionary(
            fetched_data["private_pagination"])
        # Default datasets exist in public repository only,
        # Will contain all available datasets after updating
        displayed_datasets = list(public_result.keys())
        # Exist in both public and private repository
        match_pair = []
        for id in private_result.keys():
            if id not in public_result:
                displayed_datasets.append(id)
            else:
                match_pair.append(id)
        return len(displayed_datasets), match_pair

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
        has_search_result = False

        # FILTER
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

        # SEARCH
        if input != "":
            # If input does not match any content in the database, item.search will be empty dictionary
            item.search["submitter_id"] = self.S.get_searched_datasets(input)
            if item.search != {} and ("submitter_id" not in item.filter or item.filter["submitter_id"] != []):
                has_search_result = True
                self.S.search_filter_relation(item)

        # ACCESS
        if Gen3Config.GEN3_PUBLIC_ACCESS not in item.access:
            item.access.append(Gen3Config.GEN3_PUBLIC_ACCESS)

        # ORDER
        order_type = item.order.lower()
        if order_type == "published(asc)":
            item.asc = "created_datetime"
        elif order_type == "published(desc)":
            item.desc = "created_datetime"
        elif "title" in order_type:
            # See function self.get_pagination_data
            pass
        elif "relevance" in order_type:
            # relevance is for search function applied
            # search_filter_relation has already sort the datasets
            # If search not applied and relevance order chose
            # Order the datasets with created_datetime asc order by default
            if not has_search_result:
                item.asc = "created_datetime"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"{item.order} order option not provided")

        return is_public_access_filtered
