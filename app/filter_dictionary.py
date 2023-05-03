import re

from app.data_schema import *
from app.sgqlc import SimpleGraphQLClient

FILTERS = {
    "MAPPED_AGE_CATEGORY": {
        "title": "Age Category",
        "node": "case_filter",
        "field": "age_category",
        "element": {}
    },
    "MAPPED_ANATOMICAL_STRUCTURE": {
        "title": "Anatomical Structure",
        "node": "dataset_description_filter",
        "field": "study_organ_system",
        "element": {}
    },
    "MAPPED_SEX": {
        "title": "Sex",
        "node": "case_filter",
        "field": "sex",
        "element": {}
    },
    "MAPPED_MIME_TYPE": {
        "title": "Mime Type",
        "node": "manifest_filter",
        "field": "additional_types",
        "element": {
            "Plot": ["text/vnd.abi.plot+tab-separated-values", "text/vnd.abi.plot+Tab-separated-values", "text/vnd.abi.plot+csv"],
            "Scaffold": ["application/x.vnd.abi.scaffold.meta+json", "inode/vnd.abi.scaffold+file"],
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
        "title": "Species",
        "node": "case_filter",
        "field": "species",
        "element": {
            "Cat": "Felis catus",
            "Human": "Homo sapiens",
            "Mouse": "Mus musculus",
            "Pig": "Sus scrofa",
            "Rat": "Rattus norvegicus",
        }
    }
}


class FilterGenerator:
    def generate_filter_dictionary(self, SUBMISSION):
        for element in FILTERS:
            if FILTERS[element]["element"] == {}:
                filter_element = {}
                ele_node = FILTERS[element]["node"]
                query_item = GraphQLQueryItem(node=ele_node)
                sgqlc = SimpleGraphQLClient()
                query_result = sgqlc.get_queried_result(query_item, SUBMISSION)
                ele_node = re.sub('_filter', '', ele_node)
                for ele in query_result[ele_node]:
                    value = ele[FILTERS[element]["field"]]
                    if type(value) == list and value != []:
                        for sub_value in value:
                            name = sub_value.title()
                            if name not in filter_element:
                                filter_element[name] = sub_value
                    elif type(value) == str:
                        name = value.title()
                        if value != "NA" and name not in filter_element:
                            filter_element[name] = value
                FILTERS[element]["element"] = dict(
                    sorted(filter_element.items()))
        return True
