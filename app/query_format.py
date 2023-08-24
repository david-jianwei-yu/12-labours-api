class QueryFormat(object):
    def __init__(self, f, fg):
        self.FIELDS = f.get_fields()
        self.FILTERS = fg.get_filters()

    def generate_facet_object(self, filter_facet, mapped_element):
        # Based on mapintergratedvuer map sidebar required filter format
        facet_object = {}
        facet_object["facet"] = filter_facet
        facet_object["term"] = self.FILTERS[mapped_element]["title"].capitalize()
        facet_object["facetPropPath"] = self.FILTERS[mapped_element]["node"] + \
            ">" + self.FILTERS[mapped_element]["field"]
        return facet_object

    def check_facet(self, facet_value, field, field_value):
        if type(facet_value) == str:
            # For study_organ_system
            # Array type field
            if field in self.FIELDS and facet_value in field_value:
                return True
            # For age_category/sex/species
            # String type field
            elif field_value == facet_value:
                return True
        # For additional_types
        elif type(facet_value) == list and field_value in facet_value:
            return True
        return False

    def handle_matched_facet(self, related_facet, field, field_value):
        mapped_element = f"MAPPED_{field.upper()}"
        for filter_facet, facet_value in self.FILTERS[mapped_element]["facets"].items():
            is_match = self.check_facet(facet_value, field, field_value)
            if is_match and filter_facet not in related_facet.keys():
                related_facet[filter_facet] = self.generate_facet_object(
                    filter_facet, mapped_element)

    def generate_related_facet(self, data):
        related_facet = {}
        facet_source = [
            "dataset_descriptions>study_organ_system",
            "scaffolds>additional_types",
            "plots>additional_types",
            "cases>age_category",
            "cases>sex",
            "cases>species"
        ]
        for info in facet_source:
            key = info.split(">")[0]
            field = info.split(">")[1]
            if key in data.keys() and data[key] != []:
                for ele in data[key]:
                    self.handle_matched_facet(related_facet, field, ele[field])
        return list(related_facet.values())
