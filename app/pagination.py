import re
import json

from app.config import Config
from app.data_schema import GraphQLQueryItem
from app.sgqlc import SimpleGraphQLClient
from app.filter import Filter, FIELDS
from app.search import Search
from app.filter_dictionary import FILTERS

sgqlc = SimpleGraphQLClient()
f = Filter()
s = Search()


class Pagination:
    def update_filter_values(self, filter):
        field = list(filter.keys())[0]
        value_list = []
        for ele_name in list(filter.values())[0]:
            for ele in FILTERS:
                # Check if ele can match with a exist filter object
                if FILTERS[ele]["field"] == field:
                    # Check if ele_name is a key under filter object element field
                    if ele_name in list(FILTERS[ele]["element"].keys()):
                        ele_value = FILTERS[ele]["element"][ele_name]
                        if type(ele_value) == list:
                            value_list.extend(ele_value)
                        else:
                            value_list.append(ele_value)
                    else:
                        return filter
        return {field: value_list}

    def update_pagination_item(self, item, input, SUBMISSION, SESSION):
        if item.filter != {}:
            filter_dict = {"submitter_id": []}
            temp_node_dict = {}
            for element in item.filter.values():
                filter_node = element["node"]
                filter_field = self.update_filter_values(element["filter"])
                query_item = GraphQLQueryItem(
                    node=filter_node, filter=filter_field)
                filter_node = re.sub('_filter', '', filter_node)
                filter_field = list(filter_field.keys())[0]
                # Only do fetch when there is no related temp data stored in temp_node_dict
                # or the node field type is "String"
                if filter_node not in temp_node_dict.keys() or filter_field not in FIELDS:
                    query_result = sgqlc.get_queried_result(
                        query_item, SUBMISSION)
                    # The data will be stored when the field type is an "Array"
                    # The default filter relation of the Gen3 "Array" type field is "AND"
                    # We need "OR", therefore entire node data will go through a self-written filter function
                    if filter_field in FIELDS:
                        temp_node_dict[filter_node] = query_result[filter_node]
                elif filter_node in temp_node_dict.keys() and filter_field in FIELDS:
                    query_result = temp_node_dict
                filter_dict["submitter_id"].append(f.get_filtered_datasets(
                    query_item.filter, query_result[filter_node]))
            item.filter = filter_dict
            f.filter_relation(item)

        if input != "":
            # If input does not match any content in the database, item.search will be empty dictionary
            item.search["submitter_id"] = s.get_searched_datasets(
                input, SESSION)
            if item.search != {} and ("submitter_id" not in item.filter or item.filter["submitter_id"] != []):
                s.search_filter_relation(item)

    def update_contributors(self, data):
        result = []
        if data == []:
            return result
        for ele in data:
            contributor = {
                "name": ele
            }
            result.append(contributor)
        return result

    def update_species(self, data):
        result = []
        if data == []:
            return result
        for ele in data:
            subspecies = ele.get("species")
            if subspecies != "NA":
                species_dict = FILTERS["MAPPED_SPECIES"]["element"]
                species = list(species_dict.keys())[list(
                    species_dict.values()).index(subspecies)]
                if species not in result:
                    result.append(species)
        return result

    def update_thumbnails(self, data):
        result = []
        if data == []:
            return result
        for ele in data:
            if ele["additional_types"] == None:
                result.append(ele)
        return result

    def handle_multiple_cite(self, filename, cite):
        full_path = ""
        result = {
            "path": [],
            "relative": {
                "path": []
            }
        }
        data = json.loads(re.sub("'", '"', cite))
        for ele in data:
            full_path_list = filename.split("/")
            full_path_list[-1] = ele.split("/")[-1]
            full_path = "/".join(full_path_list)
            result["path"].append(full_path)
            result["relative"]["path"].append(ele.split("/")[-1])
        return result

    # filename: (contains full file path), cite: isDerivedFrom/isDescribedBy/isSourceOf
    def handle_cite_path(self, filename, cite):
        full_path = ""
        result = {
            "path": [],
            "relative": {
                "path": []
            }
        }
        if cite != "":
            if len(cite.split(",")) > 1:
                result = self.handle_multiple_cite(filename, cite)
                return result
            full_path_list = filename.split("/")
            full_path_list[-1] = cite.split("/")[-1]
            full_path = "/".join(full_path_list)
        result["path"].append(full_path)
        result["relative"]["path"].append(cite.split("/")[-1])
        return result

    def handle_image_url(self, prefix, filename, source_of, has_image):
        full_url = prefix
        if has_image:
            if source_of != "":
                path_list = filename.split("/")
                path_list[-1] = source_of.split("/")[-1]
                filepath = "/".join(path_list)
                full_url += filepath
            else:
                full_url += filename
        else:
            return ""
        return full_url

    def handle_empty_value(self, data):
        if data == None or data == "NA":
            return ""
        return data

    def update_manifests_based(self, uuid, prefix, data, image=False):
        result = []
        for ele in data:
            item = {
                "image_url": self.handle_image_url(prefix, ele["filename"], self.handle_empty_value(ele["is_source_of"]), image),
                "additional_mimetype": {
                    "name": self.handle_empty_value(ele["additional_types"])
                },
                "datacite": {
                    "isDerivedFrom": self.handle_cite_path(ele["filename"], self.handle_empty_value(ele["is_derived_from"])),
                    "isDescribedBy": self.handle_cite_path(ele["filename"], self.handle_empty_value(ele["is_described_by"])),
                    "isSourceOf": self.handle_cite_path(ele["filename"], self.handle_empty_value(ele["is_source_of"])),
                    "supplemental_json_metadata": {
                        "description": self.handle_empty_value(ele["supplemental_json_metadata"])
                    },
                },
                "dataset": {
                    "identifier": uuid,
                    "path": ele["filename"],
                },
                "file_type": {
                    "name": self.handle_empty_value(ele["file_type"]),
                },
                "identifier": ele["id"],
                "name": ele["filename"].split("/")[-1],
            }
            result.append(item)
        return result

    def update_pagination_output(self, data):
        result = []
        for ele in data:
            dataset_id = ele["submitter_id"]
            image_url_prefix = f"{Config.BASE_URL}/data/preview/{dataset_id}/"
            item = {
                "data_url": f"{Config.PORTAL_URL}/data/browser/dataset/{dataset_id}?datasetTab=abstract",
                "source_url_prefix": f"{Config.BASE_URL}/data/download/{dataset_id}/",
                "contributors": self.update_contributors(ele["dataset_descriptions"][0]["contributor_name"]),
                "keywords": ele["dataset_descriptions"][0]["keywords"],
                "numberSamples": int(ele["dataset_descriptions"][0]["number_of_samples"][0]),
                "numberSubjects": int(ele["dataset_descriptions"][0]["number_of_subjects"][0]),
                "name": ele["dataset_descriptions"][0]["title"][0],
                "datasetId": dataset_id,
                "organs": ele["dataset_descriptions"][0]["study_organ_system"],
                "species": self.update_species(ele["cases"]),
                "plots": self.update_manifests_based(ele["id"], image_url_prefix, ele["plots"]),
                "scaffoldViews": self.update_manifests_based(ele["id"], image_url_prefix, ele["scaffoldViews"], True),
                "scaffolds": self.update_manifests_based(ele["id"], image_url_prefix, ele["scaffolds"]),
                "thumbnails": self.update_manifests_based(ele["id"], image_url_prefix, self.update_thumbnails(ele["thumbnails"]), True),
                "detailsReady": True,
            }
            result.append(item)
        return result
