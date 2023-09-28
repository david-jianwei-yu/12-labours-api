"""
Functionality for processing query related logic
- get_query_data
"""
import queue
import threading

from app.config import Gen3Config
from app.data_schema import GraphQLQueryItem


class QueryLogic:
    """
    fe -> filter editor object is required
    """

    def __init__(self, es):
        self.__es = es
        self.__public_access = [Gen3Config.GEN3_PUBLIC_ACCESS]

    def _handle_thread_fetch(self, items):
        """
        Handler for using thread to fetch data
        """
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
        result = {}
        while not queue_.empty():
            data = queue_.get()
            result.update(data)
        return result

    def _process_query_item(self, item):
        """
        Handler for generating public query item and private query item
        """
        items = []
        query_item = GraphQLQueryItem(
            node=item.node,
            filter=item.filter,
            search=item.search,
            access=self.__public_access,
        )
        items.append((query_item, "public"))
        if len(item.access) > 1:
            item.access.remove(self.__public_access[0])
            items.append((item, "private"))
        return items

    def get_query_data(self, item):
        """
        Handler for fetching data based on query item
        """
        items = self._process_query_item(item)
        # Assume there will have maximum two datasets have same submitter id at current stage
        # One for public, another one for private
        # Show private dataset by default if user has the authority
        fetch_result = self._handle_thread_fetch(items)
        if "private" in fetch_result and fetch_result["private"] != []:
            return fetch_result["private"]
        return fetch_result["public"]
