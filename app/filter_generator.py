"""
Functionality for generating the filter based on database files
- MAPPED_FILTERS
- DYNAMIC_FILTERS
- generate_private_filter
- generate_public_filter
"""
from app.config import Gen3Config
from app.data_schema import GraphQLQueryItem

MAPPED_FILTERS = {
    "MAPPED_AGE_CATEGORY": {
        "title": "age category",
        "node": "case_filter",
        "field": "age_category",
        "facets": {},
    },
    "MAPPED_STUDY_ORGAN_SYSTEM": {
        "title": "anatomical structure",
        "node": "dataset_description_filter",
        "field": "study_organ_system",
        "facets": {},
    },
    "MAPPED_SEX": {
        "title": "sex",
        "node": "case_filter",
        "field": "sex",
        "facets": {
            "Female": ["F", "Female"],
            "Male": ["M", "Male"],
        },
    },
    "MAPPED_ADDITIONAL_TYPES": {
        "title": "data type",
        "node": "manifest_filter",
        "field": "additional_types",
        "facets": {
            "Plot": ["text/vnd.abi.plot+tab-separated-values", "text/vnd.abi.plot+csv"],
            "Scaffold": [
                "application/x.vnd.abi.scaffold.meta+json",
                "inode/vnd.abi.scaffold+file",
            ],
            "Dicom": ["application/dicom"],
        },
    },
    "MAPPED_SPECIES": {
        "title": "species",
        "node": "case_filter",
        "field": "species",
        "facets": {
            "Cat": "Felis catus",
            "Human": "Homo sapiens",
            "Mouse": "Mus musculus",
            "Pig": "Sus scrofa",
            "Rat": "Rattus norvegicus",
        },
    },
    "MAPPED_PROJECT_ID": {
        "title": "access scope",
        "node": "experiment_filter",
        "field": "project_id",
        "facets": {},
    },
}

DYNAMIC_FILTERS = [
    "MAPPED_AGE_CATEGORY",
    "MAPPED_STUDY_ORGAN_SYSTEM",
    "MAPPED_PROJECT_ID",
]


class FilterGenerator:
    """
    sgqlc -> simple graphql client object is required
    """

    def __init__(self, sgqlc):
        self._sgqlc = sgqlc
        self.public_access = [Gen3Config.GEN3_PUBLIC_ACCESS]
        self.cache = {}

    def get_mapped_filter(self):
        """
        Return MAPPED_FILTERS
        """
        return MAPPED_FILTERS

    def reset_cache(self):
        """
        Cleanup self.cache
        """
        self.cache = {}

    def _update_facet(self, facets, exist_facets, value):
        """
        Handler for adding facets which not exist yet
        """
        name = value.capitalize()
        if name not in exist_facets:
            facets[name] = value

    def _update_cache(self, element_content, private_access=None):
        """
        Handler for fetching and storing data as temporary data which will be used to generate filter
        Avoid duplicate fetch
        """
        node = element_content["node"]
        query_item = GraphQLQueryItem(node=node, access=self.public_access)
        if private_access is not None:
            query_item.access = private_access
        if node not in self.cache:
            self.cache[node] = self._sgqlc.get_queried_result(query_item)

    def _handle_facet(self, element_content, private_access=None):
        """
        Handler for updating corresponding filter element facets
        """
        self._update_cache(element_content, private_access)
        facets = {}
        if private_access is not None:
            exist_facets = element_content["facets"]
        else:
            exist_facets = facets
        node = element_content["node"]
        field = element_content["field"]
        for _ in self.cache[node]:
            field_value = _[field]
            if isinstance(field_value, list) and field_value != []:
                for sub_value in field_value:
                    self._update_facet(facets, exist_facets, sub_value)
            elif isinstance(field_value, str) and field_value != "NA":
                self._update_facet(facets, exist_facets, field_value)
        return facets

    def _handle_private_access(self, access_scope):
        """
        Handler for removing public access from access, keep private access only
        """
        private_access = []
        for scope in access_scope:
            if scope != self.public_access[0]:
                private_access.append(scope)
        return private_access

    def generate_private_filter(self, access_scope):
        """
        Generator for private dataset filter
        """
        private_access = self._handle_private_access(access_scope)
        private_filter = {}
        if private_access:
            for mapped_element, element_content in MAPPED_FILTERS.items():
                if mapped_element in DYNAMIC_FILTERS:
                    private_facets = self._handle_facet(element_content, private_access)
                    if private_facets:
                        updated_facets = element_content["facets"] | private_facets
                        private_filter[mapped_element] = {
                            "title": element_content["title"].capitalize(),
                            "node": element_content["node"],
                            "field": element_content["field"],
                            "facets": dict(sorted(updated_facets.items())),
                        }
        self.reset_cache()
        return private_filter

    def generate_public_filter(self):
        """
        Generator for public dataset filter
        """
        for element_content in MAPPED_FILTERS.values():
            if not element_content["facets"]:
                public_facets = self._handle_facet(element_content)
                if not public_facets:
                    return False
                element_content["facets"] = dict(sorted(public_facets.items()))
        self.reset_cache()
        return True
