import re

from app.config import Gen3Config
from app.data_schema import *

FILTERS = {
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
        "title": "mime type",
        "node": "manifest_filter",
        "field": "additional_types",
        "facets": {
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
    "MAPPED_ANATOMICAL_STRUCTURE",
    "MAPPED_SEX",
    "MAPPED_ACCESS_SCOPE"
]


class FilterGenerator(object):
    def __init__(self, sgqlc):
        self.SGQLC = sgqlc

    def get_filters(self):
        return FILTERS

    def add_facets(self, facets, exist, value):
        name = value.capitalize()
        if name not in exist:
            facets[name] = value

    def update_filter_facets(self, temp_data, element, is_private=False):
        filter_facets = {}
        if is_private:
            exist_facets = FILTERS[element]["facets"]
        else:
            exist_facets = filter_facets
        filter_node = FILTERS[element]["node"]
        node_name = re.sub('_filter', '', filter_node)
        field = FILTERS[element]["field"]
        for ele in temp_data[filter_node][node_name]:
            field_value = ele[field]
            if type(field_value) == list and field_value != []:
                for sub_value in field_value:
                    self.add_facets(filter_facets, exist_facets, sub_value)
            elif type(field_value) == str and field_value != "NA":
                self.add_facets(filter_facets, exist_facets, field_value)
        return filter_facets

    def update_temp_node_dict(self, temp_dict, element, access=None):
        filter_node = FILTERS[element]["node"]
        query_item = GraphQLQueryItem(node=filter_node)
        if access != None:
            query_item.access = access
        if filter_node not in temp_dict:
            temp_dict[filter_node] = self.SGQLC.get_queried_result(query_item)

    def generate_private_filter(self, access):
        is_private = True
        access_scope = []
        for ele in access:
            if ele != Gen3Config.GEN3_PUBLIC_ACCESS:
                access_scope.append(ele)

        private_filter_dict = {}
        if access_scope != []:
            temp_node_dict = {}
            for mapped_element in FILTERS:
                if mapped_element in DYNAMIC_FILTERS:
                    self.update_temp_node_dict(
                        temp_node_dict, mapped_element, access_scope)

                    filter_facets = self.update_filter_facets(
                        temp_node_dict, mapped_element, is_private)
                    if filter_facets != {}:
                        updated_element = FILTERS[mapped_element]["facets"] | filter_facets
                        private_filter_dict[mapped_element] = {
                            "title": FILTERS[mapped_element]["title"].capitalize(),
                            "node": FILTERS[mapped_element]["node"],
                            "field": FILTERS[mapped_element]["field"],
                            "facets": {}
                        }
                        private_filter_dict[mapped_element]["facets"] = dict(
                            sorted(updated_element.items()))
        return private_filter_dict

    def generate_filter_dictionary(self):
        is_generated = True
        temp_node_dict = {}
        for mapped_element in FILTERS:
            if FILTERS[mapped_element]["facets"] == {}:
                # Add to temp_node_dict, avoid node data duplicate fetch
                self.update_temp_node_dict(temp_node_dict, mapped_element)

                filter_facets = self.update_filter_facets(
                    temp_node_dict, mapped_element)
                if filter_facets == {}:
                    return not is_generated

                FILTERS[mapped_element]["facets"] = dict(
                    sorted(filter_facets.items()))
        return is_generated

    def set_filter_dict(self, mapped_element, access):
        private_filter = self.generate_private_filter(access)
        if mapped_element in private_filter:
            return private_filter
        else:
            return FILTERS

    def generate_sidebar_filter_information(self, access):
        sidebar_filter_information = []
        for mapped_element in FILTERS:
            filter_dict = self.set_filter_dict(mapped_element, access)
            filter_parent = {
                "key": "",
                "label": "",
                "children": [],
            }
            filter_parent["key"] = filter_dict[mapped_element]["node"] + \
                ">" + filter_dict[mapped_element]["field"]
            filter_parent["label"] = filter_dict[mapped_element]["title"].capitalize()
            for facet_name in filter_dict[mapped_element]["facets"]:
                filter_children = {
                    "facetPropPath": "",
                    "label": "",
                }
                filter_children["facetPropPath"] = filter_parent["key"]
                filter_children["label"] = facet_name
                filter_parent["children"].append(filter_children)
            sidebar_filter_information.append(filter_parent)
        return sidebar_filter_information

    def generate_filter_information(self, access):
        filter_information = {
            "size": len(FILTERS),
            "titles": [],
            "nodes>fields": [],
            "elements": []
        }
        for mapped_element in FILTERS:
            filter_dict = self.set_filter_dict(mapped_element, access)
            filter_information["titles"].append(
                filter_dict[mapped_element]["title"].capitalize())
            filter_information["nodes>fields"].append(
                filter_dict[mapped_element]["node"] + ">" + filter_dict[mapped_element]["field"])
            filter_information["elements"].append(
                list(filter_dict[mapped_element]["facets"].keys()))
        return filter_information
