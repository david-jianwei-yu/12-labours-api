class Query(object):
    def __init__(self, fg):
        self.FILTERS = fg.get_filters()
        self.added = []
        self.facet_dict = []

    def add_matched_facet(self, field_key, field_value):
        mapped_element = f"MAPPED_{field_key.upper()}"
        for facet_key, facet_value in self.FILTERS[mapped_element]["facets"].items():
            facet_obj = {}
            is_match = False
            if type(facet_value) == str and field_value == facet_value:
                is_match = True
            elif type(facet_value) == list and field_value in facet_value:
                is_match = True
            if is_match and facet_key not in self.added:
                facet_obj["facet"] = facet_key
                facet_obj["term"] = self.FILTERS[mapped_element]["title"].capitalize()
                facet_obj["facetPropPath"] = self.FILTERS[mapped_element]["node"] + \
                    ">" + self.FILTERS[mapped_element]["field"]
                self.added.append(facet_key)
                self.facet_dict.append(facet_obj)

    def generate_related_facet(self, data):
        if "dataset_descriptions" in data.keys() and data["dataset_descriptions"] != []:
            for dataset_description in data["dataset_descriptions"]:
                self.add_matched_facet(
                    "study_organ_system", dataset_description["study_organ_system"])
        if "scaffolds" in data.keys() and data["scaffolds"] != []:
            for scaffold in data["scaffolds"]:
                self.add_matched_facet(
                    "additional_types", scaffold["additional_types"])
        if "plots" in data.keys() and data["plots"] != []:
            for plot in data["plots"]:
                self.add_matched_facet(
                    "additional_types", plot["additional_types"])
        if "cases" in data.keys() and data["cases"] != []:
            for case in data["cases"]:
                self.add_matched_facet("age_category", case["age_category"])
                self.add_matched_facet("sex", case["sex"])
                self.add_matched_facet("species", case["species"])
        return self.facet_dict
