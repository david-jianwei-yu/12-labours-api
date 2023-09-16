"""
Functionality for implementing data searching
- generate_searched_dataset
- implement_search_filter_relation
"""
import re

from fastapi import HTTPException, status
from irods.column import In, Like
from irods.models import Collection, DataObjectMeta

from app.config import iRODSConfig

SEARCHFIELD = ["TITLE", "SUBTITLE", "CONTRIBUTOR"]


class Search:
    """
    Search functionality
    es -> external service object is required
    """

    def __init__(self, es):
        self._service = es.check_service_status()

    def _handle_searched_data(self, keyword_list):
        """
        Handler for processing search result, store the number of keyword appear
        """
        dataset_dict = {}
        for keyword in keyword_list:
            try:
                query = (
                    self._service["irods"]
                    .query(Collection.name, DataObjectMeta.value)
                    .filter(In(DataObjectMeta.name, SEARCHFIELD))
                    .filter(Like(DataObjectMeta.value, f"%{keyword}%"))
                )
            except Exception as error:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
                ) from error
            # Any keyword that does not match with the database content will cause search no result
            if len(query.all()) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="There is no matched content in the database",
                )
            for result in query:
                content_list = re.findall(
                    rf"(\s{keyword}|{keyword}\s)", result[DataObjectMeta.value]
                )
                if content_list != []:
                    dataset = re.sub(
                        f"{iRODSConfig.IRODS_ROOT_PATH}/", "", result[Collection.name]
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
        keyword_list = re.findall("[a-zA-Z0-9]+", input_.lower())
        dataset_dict = self._handle_searched_data(keyword_list)
        datasets = sorted(dataset_dict, key=dataset_dict.get, reverse=True)
        return datasets

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
        else:
            item.filter["submitter_id"] = item.search["submitter_id"]
