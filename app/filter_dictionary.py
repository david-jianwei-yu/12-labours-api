import re

from app.config import Gen3Config
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

FIXED_FILTERS = [
    "MAPPED_MIME_TYPE",
    "MAPPED_SPECIES"
]
sgqlc = SimpleGraphQLClient()


class FilterGenerator:
    def generate_extra_filter(self, SUBMISSION, access):
        access_scope = []
        for ele in access:
            if ele != Gen3Config.PUBLIC_ACCESS:
                access_scope.append(ele)
        temp_node_dict = {}
        extra_filter_dict = {}
        for element in FILTERS:
            if element not in FIXED_FILTERS:
                filter_element = {}
                filter_node = FILTERS[element]["node"]
                query_item = GraphQLQueryItem(
                    node=filter_node, access=access)
                if filter_node not in temp_node_dict:
                    temp_node_dict[filter_node] = sgqlc.get_queried_result(
                        query_item, SUBMISSION)
                ele_node = re.sub('_filter', '', filter_node)
                for ele in temp_node_dict[filter_node][ele_node]:
                    value = ele[FILTERS[element]["field"]]
                    exist_element = FILTERS[element]["element"]
                    if type(value) == list and value != []:
                        for sub_value in value:
                            name = sub_value.title()
                            if name not in exist_element:
                                filter_element[name] = sub_value
                    elif type(value) == str:
                        name = value.title()
                        if value != "NA" and name not in exist_element:
                            filter_element[name] = value
                if filter_element != {}:
                    updated_element = FILTERS[element]["element"] | filter_element
                    extra_filter_dict[element] = {
                        "title": FILTERS[element]["title"],
                        "node": FILTERS[element]["node"],
                        "field": FILTERS[element]["field"],
                        "element": {}
                    }
                    extra_filter_dict[element]["element"] = dict(
                        sorted(updated_element.items()))
        return extra_filter_dict

    def generate_filter_dictionary(self, SUBMISSION):
        temp_node_dict = {}
        for element in FILTERS:
            if FILTERS[element]["element"] == {}:
                filter_element = {}
                filter_node = FILTERS[element]["node"]
                query_item = GraphQLQueryItem(node=filter_node)
                if filter_node not in temp_node_dict:
                    temp_node_dict[filter_node] = sgqlc.get_queried_result(
                        query_item, SUBMISSION)
                ele_node = re.sub('_filter', '', filter_node)
                # Add data to filter_element
                for ele in temp_node_dict[filter_node][ele_node]:
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
                if filter_element == {}:
                    return False
                else:
                    FILTERS[element]["element"] = dict(
                        sorted(filter_element.items()))
        return True
