import json
import copy
import queue
import threading

from fastapi import HTTPException, status

from app.config import Gen3Config
from app.data_schema import GraphQLQueryItem, GraphQLPaginationItem


class Pagination(object):
    def __init__(self, fg, f, s, sgqlc):
        self.FG = fg
        self.FILTER_MAP = fg.get_filter_map()
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

    def handle_order_by_dataset_description(self, filter):
        result = {}
        if "submitter_id" in filter:
            result["submitter_id"] = []
            for dataset in filter["submitter_id"]:
                result["submitter_id"].append(f"{dataset}-dataset_description")
        return result

    def get_pagination_order(self, item):
        filter_dict = self.handle_order_by_dataset_description(item.filter)
        query_item = GraphQLQueryItem(
            node="pagination_order_by_dataset_description",
            limit=item.limit,
            page=item.page,
            filter=filter_dict,
            access=item.access,
            asc=item.asc,
            desc=item.desc
        )
        if "asc" in item.order:
            query_item.asc = "title"
        elif "desc" in item.order:
            query_item.desc = "title"
        query_result = self.SGQLC.get_queried_result(query_item)

        # Include both public and private if have the access
        ordered_dataset = []
        for ele in query_result:
            dataset_id = ele["experiments"][0]["submitter_id"]
            if dataset_id not in ordered_dataset:
                ordered_dataset.append(dataset_id)
        return ordered_dataset

    def get_pagination_data(self, item, match_pair, is_public_access_filtered):
        if "title" in item.order.lower():
            # Get an ordered filter
            item.filter["submitter_id"] = self.get_pagination_order(item)
            item.page = 1

        query_item = GraphQLPaginationItem(
            limit=item.limit,
            page=item.page,
            filter=item.filter,
            access=item.access,
            order=item.order,
            asc=item.asc,
            desc=item.desc
        )
        query_result = self.SGQLC.get_queried_result(query_item)
        displayed_dataset = self.generate_dictionary(query_result)

        item.access.remove(Gen3Config.GEN3_PUBLIC_ACCESS)
        items = []
        # Query displayed datasets which have private version
        if match_pair != []:
            for dataset in match_pair:
                if dataset in displayed_dataset:
                    query_item = GraphQLQueryItem(
                        node="experiment_query",
                        filter={"submitter_id": [dataset]},
                        access=item.access
                    )
                    items.append((query_item, dataset))

        private_replacement = self.threading_fetch(items)

        if not is_public_access_filtered:
            # Replace the dataset if it has a private version
            for dataset in private_replacement.keys():
                displayed_dataset[dataset] = private_replacement[dataset][0]
        return list(displayed_dataset.values())

    def get_pagination_count(self, item):
        public_access = [Gen3Config.GEN3_PUBLIC_ACCESS]
        private_access = copy.deepcopy(item.access)
        private_access.remove(public_access[0])
        user_access = {
            "public_access": public_access,
            "private_access": private_access
        }
        # Used to get the total count for either public or private datasets
        # Public or private datasets will be processed separately
        items = []
        for key, value in user_access.items():
            pagination_count_item = GraphQLPaginationItem(
                node="experiment_pagination_count",
                filter=item.filter,
                access=value
            )
            items.append((pagination_count_item, key))

        fetched_data = self.threading_fetch(items)

        public_result = self.generate_dictionary(fetched_data["public_access"])
        private_result = self.generate_dictionary(
            fetched_data["private_access"])
        # Default datasets exist in public repository only,
        # Will contain all available datasets after updating
        displayed_dataset = list(public_result.keys())
        # Datasets which exist in both public and private repository will be added to match_pair
        # It will be used to help achieve priority presentation of private datasets
        match_pair = []
        for id in private_result.keys():
            if id not in public_result:
                displayed_dataset.append(id)
            else:
                match_pair.append(id)
        return len(displayed_dataset), match_pair

    def handle_pagination_item_filter(self, filter_field, facet_name, private_filter):
        value_list = []
        for facet in facet_name:
            # Use .capitalize() to make it non-case sensitive
            # Avoid mis-match
            facet_name = facet.capitalize()
            for mapped_element in self.FILTER_MAP:
                if mapped_element in private_filter:
                    filter_dict = private_filter
                else:
                    filter_dict = self.FILTER_MAP
                # Check if title can match with a exist filter object
                if filter_dict[mapped_element]["field"] == filter_field:
                    # Check if ele_name is a key under filter object element field
                    if facet_name not in filter_dict[mapped_element]["facets"]:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                            detail="Invalid or unauthorized facet passed in")

                    facet_value = filter_dict[mapped_element]["facets"][facet_name]
                    if type(facet_value) == list:
                        value_list.extend(facet_value)
                    else:
                        value_list.append(facet_value)
        return {filter_field: value_list}

    def update_pagination_item(self, item, input):
        is_public_access_filtered = False
        has_search_result = False

        # FILTER
        if item.filter != {}:
            private_filter = self.FG.generate_private_filter()
            items = []
            filter_dict = {"submitter_id": []}
            for node_filed, facet_name in item.filter.items():
                filter_node = node_filed.split(">")[0]
                filter_field = node_filed.split(">")[1]
                # Update filter based on authority
                valid_filter = self.handle_pagination_item_filter(
                    filter_field, facet_name, private_filter)
                query_item = GraphQLQueryItem(
                    node=filter_node,
                    filter=valid_filter
                )
                if filter_node == "experiment_filter":
                    query_item.access = valid_filter["project_id"]
                    if Gen3Config.GEN3_PUBLIC_ACCESS in query_item.access:
                        is_public_access_filtered = True
                else:
                    query_item.access = item.access
                key = json.dumps(valid_filter)
                items.append((query_item, key))

            fetched_data = self.threading_fetch(items)

            for key in fetched_data:
                filter = json.loads(key)
                filtered_dataset = self.F.get_filtered_dataset(
                    filter, fetched_data[key])
                filter_dict["submitter_id"].append(filtered_dataset)
            item.filter = filter_dict
            self.F.filter_relation(item)

        # SEARCH
        if input != "":
            # If input does not match any content in the database, item.search will be empty dictionary
            item.search["submitter_id"] = self.S.get_searched_dataset(input)
            if item.search != {} and ("submitter_id" not in item.filter or item.filter["submitter_id"] != []):
                has_search_result = True
                self.S.search_filter_relation(item)

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
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"{item.order} order option not provided")
        return is_public_access_filtered
