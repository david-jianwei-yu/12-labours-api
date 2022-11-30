import re

from app.config import iRODSConfig

from irods.column import Like, In
from irods.models import Collection, DataObjectMeta

SEARCHFIELD = [
    "title", "subtitle", "keywords", "acknowledgments",
    "contributor_affiliation", "contributor_name"
]


class Search:
    def search_filter_relation(self, item):
        # Since only search result has order, we need to update item.filter value based on search result
        # Search and filter relation will always be AND
        dataset_list = []

        if item.filter != {} and item.search != {}:
            for dataset in item.search["submitter_id"]:
                if dataset in item.filter["submitter_id"]:
                    dataset_list.append(dataset)
            item.filter["submitter_id"] = dataset_list

    def generate_dataset_list(self, SESSION, keyword_list):
        id_dict = {}
        for keyword in keyword_list:
            query = SESSION.query(Collection.name, DataObjectMeta.value).filter(
                In(DataObjectMeta.name, SEARCHFIELD)).filter(
                Like(DataObjectMeta.value, f"%{keyword}%"))
            for result in query:
                content_list = re.findall(
                    "[a-zA-Z0-9]+", result[DataObjectMeta.value])
                if keyword in content_list:
                    dataset = re.sub(
                        f"{iRODSConfig.IRODS_ENDPOINT_URL}/datasets-test/", "", result[Collection.name])
                    if dataset not in id_dict.keys():
                        id_dict[dataset] = 1
                    else:
                        id_dict[dataset] += 1
        return sorted(id_dict, key=id_dict.get, reverse=True)
