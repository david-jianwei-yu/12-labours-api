import re

from app.filter_dictionary import FILTERS


BAD_REQUEST = 400
UNAUTHORIZED = 401
NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405
INTERNAL_SERVER_ERROR = 500

# This list contains all the "Array" type fields that used as a filter
FIELDS = [
    "study_organ_system"
]


class Filter:
    def generate_filtered_datasets(self, filter, field, data):
        result = []
        for dataset in data:
            for kwd in filter[field]:
                if kwd in dataset[field]:
                    result.append(dataset)
        return result

    def get_filtered_datasets(self, filter, data):
        field = list(filter.keys())[0]
        if field in FIELDS:
            data = self.generate_filtered_datasets(filter, field, data)
        dataset_list = set()
        for record in data:
            dataset_list.add(re.findall(
                'dataset-[0-9]*-version-[0-9]*', record["submitter_id"])[0])
        return list(dataset_list)

    def filter_relation(self, item):
        nested_list = item.filter["submitter_id"]
        if item.relation == "and":  # AND relationship
            dataset_list = set(nested_list[0]).intersection(*nested_list)
        elif item.relation == "or":  # OR relationship
            dataset_list = set()
            for sublist in nested_list:
                for id in sublist:
                    dataset_list.add(id)
        item.filter["submitter_id"] = list(dataset_list)

    def generate_filter_information(self):
        filter_information = {
            "size": len(FILTERS),
            "titles": [],
            "nodes": [],
            "fields": [],
            "elements": [],
            "ids": []
        }
        for element in FILTERS:
            filter_information["titles"].append(FILTERS[element]["title"])
            filter_information["nodes"].append(FILTERS[element]["node"])
            filter_information["fields"].append(FILTERS[element]["field"])
            filter_information["elements"].append(FILTERS[element]["element"])
            for ele in FILTERS[element]["element"]:
                filter_information["ids"].append(ele)
        return filter_information
