import re

from fastapi import HTTPException

from app.config import iRODSConfig

from irods.column import Like, In
from irods.models import Collection, DataObjectMeta


BAD_REQUEST = 400
UNAUTHORIZED = 401
NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405
INTERNAL_SERVER_ERROR = 500

SEARCHFIELD = [
    "TITLE",
    "SUBTITLE",
    "CONTRIBUTOR"
]


class Search:
    def generate_dataset_dictionary(self, keyword_list, SESSION):
        dataset_dict = {}
        for keyword in keyword_list:
            query = SESSION.query(Collection.name, DataObjectMeta.value).filter(
                In(DataObjectMeta.name, SEARCHFIELD)).filter(
                Like(DataObjectMeta.value, f"%{keyword}%"))
            # Any keyword that does not match with the database content will cause a search no result
            if len(query.all()) == 0:
                dataset_dict = {}
                return dataset_dict
            for result in query:
                content_list = re.findall(
                    '[a-zA-Z0-9]+', result[DataObjectMeta.value])
                if keyword in content_list:
                    dataset = re.sub(
                        f'{iRODSConfig.IRODS_ENDPOINT_URL}/', '', result[Collection.name])
                    if dataset not in dataset_dict.keys():
                        dataset_dict[dataset] = 1
                    else:
                        dataset_dict[dataset] += 1
                # Any keyword that does not match with the database content will cause a search no result
                else:
                    dataset_dict = {}
                    return dataset_dict
        return dataset_dict

    # The dataset list order is based on how the dataset content is relevant to the input string.
    def get_searched_datasets(self, input, SESSION):
        try:
            keyword_list = re.findall('[a-zA-Z0-9]+', input.lower())
            dataset_dict = self.generate_dataset_dictionary(
                keyword_list, SESSION)
            dataset_list = sorted(
                dataset_dict, key=dataset_dict.get, reverse=True)
        except Exception as e:
            raise HTTPException(
                status_code=INTERNAL_SERVER_ERROR, detail=str(e))

        if dataset_list == []:
            raise HTTPException(status_code=NOT_FOUND,
                                detail="There is no matched content in the database")
        else:
            return dataset_list

    def search_filter_relation(self, item):
        # Since only search result has order, we need to update item.filter value based on search result
        # The relationship between search and filter will always be AND
        if item.filter != {}:
            dataset_list = []
            for dataset in item.search["submitter_id"]:
                if dataset in item.filter["submitter_id"]:
                    dataset_list.append(dataset)
            item.filter["submitter_id"] = dataset_list
        else:
            item.filter["submitter_id"] = item.search["submitter_id"]
