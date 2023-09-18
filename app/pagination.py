"""
Functionality for processing pagination related logic
- get_pagination_data
- get_pagination_count
- process_pagination_item
"""
import copy
import json
import queue
import threading

from fastapi import HTTPException, status

from app.config import Gen3Config
from app.data_schema import GraphQLPaginationItem, GraphQLQueryItem


class Pagination:
    """
    fg -> filter generator object is required
    f -> filter object is required
    s -> search object is required
    es -> external service object is required
    """

    def __init__(self, fg, f, s, es):
        self._fg = fg
        self._mapped_filter = fg.get_mapped_filter()
        self._f = f
        self._s = s
        self._es = es
        self.public_access = [Gen3Config.GEN3_PUBLIC_ACCESS]

    def _handle_dataset(self, data):
        """
        Handler for generating dataset dictionary
        """
        dataset_dict = {}
        for ele in data:
            dataset_id = ele["submitter_id"]
            if dataset_id not in dataset_dict:
                dataset_dict[dataset_id] = ele
        return dataset_dict

    def _handle_thread_fetch(self, items):
        """
        Handler for using thread to fetch data
        """
        queue_ = queue.Queue()
        threads_pool = []
        for args in items:
            thread = threading.Thread(
                target=self._es.process_gen3_graphql_query, args=(*args, queue_)
            )
            threads_pool.append(thread)
            thread.start()
        for thread in threads_pool:
            thread.join()
        result = {}
        while not queue_.empty():
            data = queue_.get()
            result.update(data)
        return result

    def _handle_order_by_dataset_description(self, filter_):
        """
        Handler for updating submitter_id for order by dataset description
        """
        result = {}
        if "submitter_id" in filter_:
            result["submitter_id"] = []
            for dataset in filter_["submitter_id"]:
                result["submitter_id"].append(f"{dataset}-dataset_description")
        return result

    def _handle_pagination_order(self, item):
        """
        Handler for updating pagination data order
        """
        query_item = GraphQLQueryItem(
            node="pagination_order_by_dataset_description",
            limit=item.limit,
            page=item.page,
            filter=self._handle_order_by_dataset_description(item.filter),
            access=item.access,
            asc=item.asc,
            desc=item.desc,
        )
        if "asc" in item.order:
            query_item.asc = "title"
        elif "desc" in item.order:
            query_item.desc = "title"
        # Include both public and private if have the access
        ordered_datasets = []
        for ele in self._es.process_gen3_graphql_query(query_item):
            dataset_id = ele["experiments"][0]["submitter_id"]
            if dataset_id not in ordered_datasets:
                ordered_datasets.append(dataset_id)
        return ordered_datasets

    def get_pagination_data(self, item, match_pair, is_public_access_filtered):
        """
        Handler for fetching data based on pagination item
        """
        if "title" in item.order.lower():
            # Get an ordered filter
            item.filter["submitter_id"] = self._handle_pagination_order(item)
            item.page = 1
        query_item = GraphQLPaginationItem(
            limit=item.limit,
            page=item.page,
            filter=item.filter,
            access=item.access,
            order=item.order,
            asc=item.asc,
            desc=item.desc,
        )
        displayed_dataset = self._handle_dataset(
            self._es.process_gen3_graphql_query(query_item)
        )
        item.access.remove(self.public_access[0])
        items = []
        # Query displayed datasets which have private version
        if match_pair != []:
            for dataset in match_pair:
                if dataset in displayed_dataset:
                    query_item = GraphQLQueryItem(
                        node="experiment_query",
                        filter={"submitter_id": [dataset]},
                        access=item.access,
                    )
                    items.append((query_item, dataset))
        if not is_public_access_filtered:
            # Replace the dataset if it has a private version
            for dataset, data in self._handle_thread_fetch(items).items():
                displayed_dataset[dataset] = data[0]
        return list(displayed_dataset.values())

    def get_pagination_count(self, item):
        """
        Handler for processing the number of data based on pagination item
        """
        private_access = copy.deepcopy(item.access)
        private_access.remove(self.public_access[0])
        user_access = {
            "public_access": self.public_access,
            "private_access": private_access,
        }
        # Used to get the total count for either public or private datasets
        # Public or private datasets will be processed separately
        items = []
        for key, value in user_access.items():
            pagination_count_item = GraphQLPaginationItem(
                node="experiment_pagination_count", filter=item.filter, access=value
            )
            items.append((pagination_count_item, key))
        fetched_data = self._handle_thread_fetch(items)
        public_result = self._handle_dataset(fetched_data["public_access"])
        private_result = self._handle_dataset(fetched_data["private_access"])
        # Default datasets exist in public repository only,
        # Will contain all available datasets after updating
        displayed_dataset = list(public_result.keys())
        # Datasets which exist in both public and private repository will be added to match_pair
        # It will be used to help achieve priority presentation of private datasets
        match_pair = []
        for dataset_id in private_result:
            if dataset_id not in public_result:
                displayed_dataset.append(dataset_id)
            else:
                match_pair.append(dataset_id)
        return len(displayed_dataset), match_pair

    def _handle_pagination_item_filter(self, filter_field, facets, private_filter):
        """
        Handler for updating filter in pagination item
        """
        value_list = []
        for facet in facets:
            # Use .capitalize() to make it non-case sensitive
            # Avoid mis-match
            facet_name = facet.capitalize()
            for mapped_element in self._mapped_filter:
                if mapped_element in private_filter:
                    content = private_filter[mapped_element]
                else:
                    content = self._mapped_filter[mapped_element]
                # Check if title can match with a exist filter object
                if content["field"] == filter_field:
                    # Check if ele_name is a key under filter object element field
                    if facet_name not in content["facets"]:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid or unauthorized facet passed in",
                        )

                    facet_value = content["facets"][facet_name]
                    if isinstance(facet_value, list):
                        value_list.extend(facet_value)
                    else:
                        value_list.append(facet_value)
        return {filter_field: value_list}

    def _handle_access(self, access_scope):
        """
        Handler for generating private access
        """
        private_access = []
        for scope in access_scope:
            if scope != self.public_access[0]:
                private_access.append(scope)
        return private_access

    def process_pagination_item(self, item, input_):
        """
        Handler for process pagination item to fit the query code generator format
        """
        is_public_access_filtered = False
        has_search_result = False

        # FILTER
        if item.filter != {}:
            private_filter = self._fg.generate_private_filter(
                self._handle_access(item.access)
            )
            items = []
            filter_dict = {"submitter_id": []}
            for node_filed, facets in item.filter.items():
                filter_node = node_filed.split(">")[0]
                filter_field = node_filed.split(">")[1]
                # Update filter based on authority
                valid_filter = self._handle_pagination_item_filter(
                    filter_field, facets, private_filter
                )
                query_item = GraphQLQueryItem(
                    node=filter_node, filter=valid_filter, access=self.public_access
                )
                if filter_node == "experiment_filter":
                    query_item.access = valid_filter["project_id"]
                    if self.public_access[0] in query_item.access:
                        is_public_access_filtered = True
                else:
                    query_item.access = item.access
                items.append((query_item, json.dumps(valid_filter)))
            for filter_, related_data in self._handle_thread_fetch(items).items():
                filter_dict["submitter_id"].append(
                    self._f.generate_filtered_dataset(json.loads(filter_), related_data)
                )
            item.filter = filter_dict
            self._f.implement_filter_relation(item)

        # SEARCH
        if input_ != "":
            # If input does not match any content in the database, item.search will be empty
            item.search["submitter_id"] = self._s.generate_searched_dataset(input_)
            if item.search != {} and (
                "submitter_id" not in item.filter or item.filter["submitter_id"] != []
            ):
                has_search_result = True
                self._s.implement_search_filter_relation(item)

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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{item.order} order option not provided",
            )
        return is_public_access_filtered
