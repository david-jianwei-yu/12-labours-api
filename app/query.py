class Query(object):
    def __init__(self, fg):
        self.FG = fg

    def add_matched_facet(self, FILTERS, field, data_type, exist_facet, related_facet):
        mapped_element = f"MAPPED_{field.upper()}"
        for key, value in FILTERS[mapped_element]["facets"].items():
            facet_obj = {}
            if value == data_type[field] and key not in exist_facet:
                facet_obj["facet"] = key
                facet_obj["term"] = FILTERS[mapped_element]["title"]
                facet_obj["facetPropPath"] = FILTERS[mapped_element]["node"] + ">" + FILTERS[mapped_element]["field"]
                exist_facet.append(key)
                related_facet.append(facet_obj)

    def generate_related_facet(self, data):
        FILTERS = self.FG.get_filters()
        exist_facet = []
        related_facet = []
        if "dataset_descriptions" in data.keys() and data["dataset_descriptions"] != []:
            for dataset_description in data["dataset_descriptions"]:
                self.add_matched_facet(FILTERS, "study_organ_system", dataset_description, exist_facet, related_facet)
        if "scaffolds" in data.keys() and data["scaffolds"] != []:
            for scaffold in data["scaffolds"]:
                self.add_matched_facet(FILTERS, "additional_types", scaffold, exist_facet, related_facet)
        if "cases" in data.keys() and data["cases"] != []:
            for case in data["cases"]:
                self.add_matched_facet(FILTERS, "age_category", case, exist_facet, related_facet)
                self.add_matched_facet(FILTERS, "sex", case, exist_facet, related_facet)
                self.add_matched_facet(FILTERS, "species", case, exist_facet, related_facet)
        return related_facet
    