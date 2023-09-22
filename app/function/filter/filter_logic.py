"""
Functionality for implementing data filtering
- generate_filtered_dataset
- implement_filter_relation
"""
# This list contains all the "Array" type fields that used as a filter
FIELDS = ["study_organ_system"]


class FilterLogic:
    """
    Filter logic functionality
    """

    def _handle_filtered_data(self, filter_, data):
        """
        Handler for processing data with field in FIELDS
        """
        field = list(filter_.keys())[0]
        if field in FIELDS:
            matched_data = []
            for _ in data:
                for value in filter_[field]:
                    if value in _[field]:
                        matched_data.append(_)
            data = matched_data
        return data

    def generate_filtered_dataset(self, filter_, data):
        """
        Handler for generating the filtered dataset
        """
        datasets = []
        filtered_result = self._handle_filtered_data(filter_, data)
        for _ in filtered_result:
            if "experiments" in _:
                datasets.append(_["experiments"][0]["submitter_id"])
            else:
                # Implement filter in experiment node
                datasets.append(_["submitter_id"])
        return datasets

    def implement_filter_relation(self, item):
        """
        Handler for processing different filter relation types
        """
        nested_list = item.filter["submitter_id"]
        if item.relation == "and":  # AND relationship
            datasets = set(nested_list[0]).intersection(*nested_list)
        elif item.relation == "or":  # OR relationship
            datasets = set()
            for ids_list in nested_list:
                for dataset_id in ids_list:
                    datasets.add(dataset_id)
        item.filter["submitter_id"] = list(datasets)
