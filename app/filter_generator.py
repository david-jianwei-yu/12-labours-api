from app.config import Gen3Config
from app.data_schema import GraphQLQueryItem

MAPPED_FILTERS = {
    "MAPPED_AGE_CATEGORY": {
        "title": "age category",
        "node": "case_filter",
        "field": "age_category",
        "facets": {}
    },
    "MAPPED_STUDY_ORGAN_SYSTEM": {
        "title": "anatomical structure",
        "node": "dataset_description_filter",
        "field": "study_organ_system",
        "facets": {}
    },
    "MAPPED_SEX": {
        "title": "sex",
        "node": "case_filter",
        "field": "sex",
        "facets": {}
    },
    "MAPPED_ADDITIONAL_TYPES": {
        "title": "data type",
        "node": "manifest_filter",
        "field": "additional_types",
        "facets": {
            "Plot": ["text/vnd.abi.plot+tab-separated-values", "text/vnd.abi.plot+csv"],
            "Scaffold": ["application/x.vnd.abi.scaffold.meta+json", "inode/vnd.abi.scaffold+file"],
            "Dicom": ["application/dicom"],
            # "CSV": ["text/csv"],
            # "SEGMENTATION_FILES": ["application/vnd.mbfbioscience.metadata+xml", "application/vnd.mbfbioscience.neurolucida+xml"],
            # "CONTEXT_FILE": ["application/x.vnd.abi.context-information+json"],
            # "SCAFFOLD_VIEW_FILE": ["application/x.vnd.abi.scaffold.view+json", "inode/vnd.abi.scaffold.view+file"],
            # "SIMULATION_FILE": ["application/x.vnd.abi.simulation+json"],
            # "THUMBNAIL_IMAGE": ["image/x.vnd.abi.thumbnail+jpeg", "inode/vnd.abi.scaffold+thumbnail", "inode/vnd.abi.scaffold.thumbnail+file"],
            # "SCAFFOLD_DIR": ["inode/vnd.abi.scaffold+directory"],
            # "COMMON_IMAGES": ["image/png", "image/jpeg"],
            # "tiff-image": ["image/tiff", "image/tif"],
            # "BIOLUCIDA_3D": ["image/jpx", "image/vnd.ome.xml+jpx"],
            # "BIOLUCIDA_2D": ["image/jp2", "image/vnd.ome.xml+jp2"],
            # "VIDEO": ["video/mp4"],
        }
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
        }
    },
    "MAPPED_PROJECT_ID": {
        "title": "access scope",
        "node": "experiment_filter",
        "field": "project_id",
        "facets": {}
    }
}

DYNAMIC_FILTERS = [
    "MAPPED_AGE_CATEGORY",
    "MAPPED_STUDY_ORGAN_SYSTEM",
    "MAPPED_SEX",
    "MAPPED_PROJECT_ID"
]


class FilterGenerator(object):
    def __init__(self, sgqlc):
        self.SGQLC = sgqlc
        self.public_access = [Gen3Config.GEN3_PUBLIC_ACCESS]

    def get_mapped_filter(self):
        return MAPPED_FILTERS

    def add_facet(self, filter_facets, exist_facets, value):
        name = value.capitalize()
        if name not in exist_facets:
            filter_facets[name] = value

    def update_filter_facet(self, temp_data, mapped_element, private_access=None):
        filter_facets = {}
        if private_access != None:
            exist_facets = MAPPED_FILTERS[mapped_element]["facets"]
        else:
            exist_facets = filter_facets
        filter_node = MAPPED_FILTERS[mapped_element]["node"]
        field = MAPPED_FILTERS[mapped_element]["field"]
        for ele in temp_data[filter_node]:
            field_value = ele[field]
            if type(field_value) == list and field_value != []:
                for sub_value in field_value:
                    self.add_facet(filter_facets, exist_facets, sub_value)
            elif type(field_value) == str and field_value != "NA":
                self.add_facet(filter_facets, exist_facets, field_value)
        return filter_facets

    def update_temp_data(self, temp_data, mapped_element, private_access=None):
        filter_node = MAPPED_FILTERS[mapped_element]["node"]
        query_item = GraphQLQueryItem(
            node=filter_node,
            access=self.public_access
        )
        if private_access != None:
            query_item.access = private_access
        if filter_node not in temp_data:
            temp_data[filter_node] = self.SGQLC.get_queried_result(query_item)

    def handle_access(self, access_scope):
        private_access = []
        for scope in access_scope:
            if scope != self.public_access[0]:
                private_access.append(scope)
        return private_access

    def generate_private_filter(self, access_scope):
        private_access = self.handle_access(access_scope)
        private_filter = {}
        if private_access != []:
            temp_data = {}
            for mapped_element in MAPPED_FILTERS:
                if mapped_element in DYNAMIC_FILTERS:
                    self.update_temp_data(
                        temp_data, mapped_element, private_access)
                    filter_facets = self.update_filter_facet(
                        temp_data, mapped_element, private_access)
                    if filter_facets != {}:
                        updated_element = MAPPED_FILTERS[mapped_element]["facets"] | filter_facets
                        private_filter[mapped_element] = {
                            "title": MAPPED_FILTERS[mapped_element]["title"].capitalize(),
                            "node": MAPPED_FILTERS[mapped_element]["node"],
                            "field": MAPPED_FILTERS[mapped_element]["field"],
                            "facets": {}
                        }
                        private_filter[mapped_element]["facets"] = dict(
                            sorted(updated_element.items()))
        return private_filter

    def set_filter(self, mapped_element, access_scope):
        private_filter = self.generate_private_filter(access_scope)
        if mapped_element in private_filter:
            return private_filter
        else:
            return MAPPED_FILTERS

    def generate_public_filter(self):
        temp_data = {}
        for mapped_element in MAPPED_FILTERS:
            if MAPPED_FILTERS[mapped_element]["facets"] == {}:
                # Add to temp_data, avoid node data duplicate fetch
                self.update_temp_data(temp_data, mapped_element)
                filter_facets = self.update_filter_facet(
                    temp_data, mapped_element)
                if filter_facets == {}:
                    return False

                MAPPED_FILTERS[mapped_element]["facets"] = dict(
                    sorted(filter_facets.items()))
        return True
