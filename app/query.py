class Query(object):
    def __init__(self, fg):
        self.FILTERS = fg.get_filters()
        self.exist = []
        self.facet_dict = []

    def add_matched_facet(self, field, data_type):
        mapped_element = f"MAPPED_{field.upper()}"
        for key, value in self.FILTERS[mapped_element]["facets"].items():
            facet_obj = {}
            if value == data_type[field] and key not in self.exist:
                facet_obj["facet"] = key
                facet_obj["term"] = self.FILTERS[mapped_element]["title"]
                facet_obj["facetPropPath"] = self.FILTERS[mapped_element]["node"] + \
                    ">" + self.FILTERS[mapped_element]["field"]
                self.exist.append(key)
                self.facet_dict.append(facet_obj)

    def generate_related_facet(self, data):
        if "dataset_descriptions" in data.keys() and data["dataset_descriptions"] != []:
            for dataset_description in data["dataset_descriptions"]:
                self.add_matched_facet(
                    "study_organ_system", dataset_description)
        if "scaffolds" in data.keys() and data["scaffolds"] != []:
            for scaffold in data["scaffolds"]:
                self.add_matched_facet("additional_types", scaffold)
        if "plots" in data.keys() and data["plots"] != []:
            for plot in data["plots"]:
                self.add_matched_facet("additional_types", plot)
        if "cases" in data.keys() and data["cases"] != []:
            for case in data["cases"]:
                self.add_matched_facet("age_category", case)
                self.add_matched_facet("sex", case)
                self.add_matched_facet("species", case)
        return self.facet_dict
