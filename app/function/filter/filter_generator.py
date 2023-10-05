"""
Functionality for generating the filter based on database files
- generate_private_filter
- generate_public_filter
"""
import queue
import threading

from app.config import Gen3Config
from app.data_schema import GraphQLQueryItem

DYNAMIC_FILTERS = [
    "MAPPED_AGE_CATEGORY",
    "MAPPED_STUDY_ORGAN_SYSTEM",
    "MAPPED_PROJECT_ID",
]


class FilterGenerator:
    """
    fe -> filter editor object is required
    es -> external service object is required
    """

    def __init__(self, fe, es):
        self.__fe = fe
        self.__filter_cache = fe.cache_loader()
        self.__es = es
        self.__public_access = [Gen3Config.GEN3_PUBLIC_ACCESS]
        self.__cache = {}

    def _reset_cache(self):
        """
        Cleanup self.__cache
        """
        self.__cache = {}

    def _update_facet(self, facets, exist_facets, value):
        """
        Handler for adding facets which not exist yet
        """
        name = value.capitalize()
        if name not in exist_facets:
            facets[name] = value

    def _handle_facet(self, element_content, private_access=None):
        """
        Handler for updating corresponding filter element facets
        """
        facets = {}
        exist_facets = facets
        if private_access is not None:
            exist_facets = element_content["facets"]
        node = element_content["node"]
        field = element_content["field"]
        for _ in self.__cache[node]:
            field_value = _[field]
            if isinstance(field_value, list) and field_value != []:
                for sub_value in field_value:
                    self._update_facet(facets, exist_facets, sub_value)
            elif isinstance(field_value, str) and field_value != "NA":
                self._update_facet(facets, exist_facets, field_value)
        return facets

    def _handle_filter_query_item(self, private_access=None):
        items = []
        for mapped_element in DYNAMIC_FILTERS:
            node = self.__filter_cache[mapped_element]["node"]
            query_item = GraphQLQueryItem(
                node=node,
                access=self.__public_access,
            )
            if private_access is not None:
                query_item.access = private_access
            items.append((query_item, node))
        return items

    def _update_cache(self, private_access=None):
        """
        Handler for using thread to update data cache
        """
        items = self._handle_filter_query_item(private_access)
        queue_ = queue.Queue()
        threads_pool = []
        for args in items:
            thread = threading.Thread(
                target=self.__es.get("gen3").process_graphql_query, args=(*args, queue_)
            )
            threads_pool.append(thread)
            thread.start()
        for thread in threads_pool:
            thread.join()
        while not queue_.empty():
            self.__cache.update(queue_.get())

    def _handle_private_access(self, access_scope):
        """
        Handler for removing public access from access, keep private access only
        """
        private_access = []
        for scope in access_scope:
            if scope != self.__public_access[0]:
                private_access.append(scope)
        return private_access

    def generate_private_filter(self, access_scope):
        """
        Generator for private dataset filter
        """
        private_access = self._handle_private_access(access_scope)
        private_filter = {}
        if private_access:
            self._update_cache(private_access)
            for mapped_element, element_content in self.__filter_cache.items():
                if mapped_element in DYNAMIC_FILTERS:
                    private_facets = self._handle_facet(element_content, private_access)
                    if private_facets:
                        updated_facets = element_content["facets"] | private_facets
                        private_filter[mapped_element] = {
                            "title": element_content["title"].capitalize(),
                            "node": element_content["node"],
                            "field": element_content["field"],
                            "facets": dict(sorted(updated_facets.items())),
                        }
        self._reset_cache()
        return private_filter

    def generate_public_filter(self):
        """
        Generator for public dataset filter
        """
        self._update_cache()
        for mapped_element, element_content in self.__filter_cache.items():
            if mapped_element in DYNAMIC_FILTERS:
                public_facets = self._handle_facet(element_content)
                if not public_facets:
                    return False
                element_content["facets"] = dict(sorted(public_facets.items()))
        self._reset_cache()
        self.__fe.update_filter_cache(self.__filter_cache)
        return True
