import re

from fastapi import HTTPException, status
from irods.column import Like, In
from irods.models import Collection, DataObjectMeta

from app.config import iRODSConfig

SEARCHFIELD = [
    "TITLE",
    "SUBTITLE",
    "CONTRIBUTOR"
]


class Search(object):
    def __init__(self, session):
        self.SESSION = session

    def handle_searched_dataset(self, keyword_list):
        dataset_dict = {}
        for keyword in keyword_list:
            try:
                query = self.SESSION.query(Collection.name, DataObjectMeta.value).filter(
                    In(DataObjectMeta.name, SEARCHFIELD)).filter(
                    Like(DataObjectMeta.value, f"%{keyword}%"))
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail=str(e))
            # Any keyword that does not match with the database content will cause a search no result
            if len(query.all()) == 0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="There is no matched content in the database")

            for result in query:
                content_list = re.findall(
                    fr'(\s{keyword}|{keyword}\s)',
                    result[DataObjectMeta.value]
                )
                if content_list != []:
                    dataset = re.sub(
                        f'{iRODSConfig.IRODS_ROOT_PATH}/',
                        '',
                        result[Collection.name]
                    )
                    if dataset not in dataset_dict:
                        dataset_dict[dataset] = 1
                    else:
                        dataset_dict[dataset] += 1
        return dataset_dict

    # The dataset list order is based on how the dataset content is relevant to the input string.
    def get_searched_dataset(self, input):
        keyword_list = re.findall('[a-zA-Z0-9]+', input.lower())
        dataset_dict = self.handle_searched_dataset(keyword_list)
        dataset_list = sorted(dataset_dict, key=dataset_dict.get, reverse=True)
        return dataset_list

    def search_filter_relation(self, item):
        # Search result has order, we need to update item.filter value based on search result
        # The relationship between search and filter will always be AND
        if item.filter != {}:
            dataset_list = []
            for dataset_id in item.search["submitter_id"]:
                if dataset_id in item.filter["submitter_id"]:
                    dataset_list.append(dataset_id)
            item.filter["submitter_id"] = dataset_list
        else:
            item.filter["submitter_id"] = item.search["submitter_id"]
