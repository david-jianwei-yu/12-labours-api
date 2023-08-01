from app.data_schema import *

# This list contains all the "Array" type fields that used as a filter
FIELDS = [
    "study_organ_system"
]


class Filter(object):
    def __init__(self, fg):
        self.FG = fg

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
        dataset_list = []
        for record in data:
            if "experiments" in record:
                dataset_list.append(record["experiments"][0]["submitter_id"])
            else:
                # Implement filter in experiment node
                dataset_list.append(record["submitter_id"])
        return dataset_list

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
