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
            query_item = GraphQLQueryItem()
            filter_dict = {"submitter_id": []}
            temp_node_dict = {}
            for element in item.filter.values():
                query_item.node = element["node"]
                query_item.filter = self.update_filter_values(
                    element["filter"])
                filter_node = re.sub('_filter', '', query_item.node)
                filter_field = list(query_item.filter.keys())[0]
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

    def handle_empty_value(self, data):
        if data == None or data == "NA":
            return ""
        return data

    def handle_multiple_cite(self, filename, cite):
        full_path = ""
        path_object = {
            "path": [],
            "relative": {
                "path": []
            }
        }
        for ele in json.loads(re.sub("'", '"', cite)):
            full_path_list = filename.split("/")
            full_path_list[-1] = ele.split("/")[-1]
            full_path = "/".join(full_path_list)
            path_object["path"].append(full_path)
            path_object["relative"]["path"].append(ele.split("/")[-1])
        return path_object

    # filename: (contains full file path), data: isDerivedFrom/isDescribedBy/isSourceOf
    def handle_path(self, filename, data):
        full_path = ""
        path_object = {
            "path": [],
            "relative": {
                "path": []
            }
        }
        if data != "":
            if len(data.split(",")) > 1:
                path_object = self.handle_multiple_cite(filename, data)
                return path_object
            full_path_list = filename.split("/")
            full_path_list[-1] = data.split("/")[-1]
            full_path = "/".join(full_path_list)
        path_object["path"].append(full_path)
        path_object["relative"]["path"].append(data.split("/")[-1])
        return path_object

    def handle_image_url(self, filetype, datasetId, filename, source_of):
        url_suffix = f"{Config.BASE_URL}/data/preview/{datasetId}"
        if filetype == "scaffoldViews" or filetype == "thumbnails":
            if source_of != "":
                path_list = filename.split("/")
                path_list[-1] = source_of.split("/")[-1]
                filepath = "/".join(path_list)
                url_suffix += f"/{filepath}"
            else:
                url_suffix += f"/{filename}"
        return url_suffix

    def update_manifests_based(self, filetype, uuid, datasetId, data):
        items = []
        for ele in data:
            item = {
                "image_url": self.handle_image_url(filetype, datasetId, ele["filename"], self.handle_empty_value(ele["is_source_of"])),
                "source_url_prefix": f"{Config.BASE_URL}/data/download/{datasetId}/",
                "additional_mimetype": {
                    "name": self.handle_empty_value(ele["additional_types"])
                },
                "datacite": {
                    "isDerivedFrom": self.handle_path(ele["filename"], self.handle_empty_value(ele["is_derived_from"])),
                    "isDescribedBy": self.handle_path(ele["filename"], self.handle_empty_value(ele["is_described_by"])),
                    "isSourceOf": self.handle_path(ele["filename"], self.handle_empty_value(ele["is_source_of"])),
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
            items.append(item)
        return items

    def update_pagination_output(self, result):
        items = []
        for ele in result:
            item = {
                "data_url": f"{Config.PORTAL_URL}/data/browser/dataset/" + ele["submitter_id"] + "?datasetTab=abstract",
                "contributors": ele["dataset_descriptions"][0]["contributor_name"],
                "keywords": ele["dataset_descriptions"][0]["keywords"],
                "numberSamples": int(ele["dataset_descriptions"][0]["number_of_samples"][0]),
                "numberSubjects": int(ele["dataset_descriptions"][0]["number_of_subjects"][0]),
                "name": ele["dataset_descriptions"][0]["title"][0],
                "datasetId": ele["submitter_id"],
                "organs": ele["dataset_descriptions"][0]["study_organ_system"],
                "species": self.update_species(ele["cases"]),
                "plots": self.update_manifests_based("plots", ele["id"], ele["submitter_id"], ele["plots"]),
                "scaffoldViews": self.update_manifests_based("scaffoldViews", ele["id"], ele["submitter_id"], ele["scaffoldViews"]),
                "scaffolds": self.update_manifests_based("scaffolds", ele["id"], ele["submitter_id"], ele["scaffolds"]),
                "thumbnails": self.update_manifests_based("thumbnails", ele["id"], ele["submitter_id"], self.update_thumbnails(ele["thumbnails"])),
            }
            items.append(item)
        return items
