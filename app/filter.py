# This list contains all the "Array" type fields that used as a filter
FIELDS = [
    "study_organ_system"
]


class Filter(object):
    def handle_filtered_dataset(self, filter, data):
        field = list(filter.keys())[0]
        if field in FIELDS:
            dataset = []
            for ele in data:
                for value in filter[field]:
                    if value in ele[field]:
                        dataset.append(ele)
            data = dataset
        return data

    def get_filtered_dataset(self, filter, data):
        data = self.handle_filtered_dataset(filter, data)
        dataset_list = []
        for ele in data:
            if "experiments" in ele:
                dataset_list.append(ele["experiments"][0]["submitter_id"])
            else:
                # Implement filter in experiment node
                dataset_list.append(ele["submitter_id"])
        return dataset_list

    def filter_relation(self, item):
        nested_list = item.filter["submitter_id"]
        if item.relation == "and":  # AND relationship
            dataset_list = set(nested_list[0]).intersection(*nested_list)
        elif item.relation == "or":  # OR relationship
            dataset_list = set()
            for ids_list in nested_list:
                for dataset_id in ids_list:
                    dataset_list.add(dataset_id)
        item.filter["submitter_id"] = list(dataset_list)
