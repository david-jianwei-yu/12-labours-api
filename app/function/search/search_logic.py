"""
Functionality for implementing data searching
- generate_searched_dataset
- implement_search_filter_relation
"""
import re

from irods.models import Collection, DataObjectMeta

from app.config import iRODSConfig

SEARCHFIELD = ["TITLE", "SUBTITLE", "CONTRIBUTOR"]


class SearchLogic:
    """
    Search logic functionality
    es -> external service object is required
    """

    def __init__(self, es):
        self.__es = es
        self.__search = SEARCHFIELD

    def _handle_searched_data(self, keyword_list):
        """
        Handler for processing search result, store the number of keyword appear
        """
        dataset_dict = {}
        for keyword in keyword_list:
            search_result = self.__es.get("irods").process_keyword_search(
                self.__search, keyword
            )
            for _ in search_result:
                content_list = re.findall(
                    rf"(\s{keyword}|{keyword}\s)", _[DataObjectMeta.value]
                )
                if content_list != []:
                    dataset = re.sub(
                        f"{iRODSConfig.IRODS_ROOT_PATH}/", "", _[Collection.name]
                    )
                    if dataset not in dataset_dict:
                        dataset_dict[dataset] = 1
                    else:
                        dataset_dict[dataset] += 1
        return dataset_dict

    # The datasets order is based on how the dataset content is relevant to the input_ string.
    def generate_searched_dataset(self, input_):
        """
        Handler for generating the searched dataset
        """
        dataset_dict = {"submitter_id": []}
        keyword_list = re.findall("[a-zA-Z0-9]+", input_.lower())
        searched_result = self._handle_searched_data(keyword_list)
        dataset_dict["submitter_id"] = sorted(
            searched_result, key=searched_result.get, reverse=True
        )
        return dataset_dict

    def implement_search_filter_relation(self, item):
        """
        Handler for processing relation between search and filter
        """
        # Search result has order, we need to update item.filter value based on search result
        # The relationship between search and filter will always be AND
        if item.filter != {}:
            datasets = []
            for dataset_id in item.search["submitter_id"]:
                if dataset_id in item.filter["submitter_id"]:
                    datasets.append(dataset_id)
            item.filter["submitter_id"] = datasets
            return datasets
        item.filter["submitter_id"] = item.search["submitter_id"]
        return item.search["submitter_id"]
