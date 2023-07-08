import re
import json
import copy
import queue
import threading

from app.config import Gen3Config
from app.data_schema import GraphQLQueryItem, GraphQLPaginationItem
from app.sgqlc import SimpleGraphQLClient
from app.filter import Filter, FIELDS
from app.search import Search
from app.filter_dictionary import FilterGenerator, FILTERS

SUBMISSION = None
f = Filter()
s = Search()
sgqlc = SimpleGraphQLClient()
fg = FilterGenerator()


class Pagination:
    def generate_dataset_dictionary(self, data):
        dataset_dict = {}
        for ele in data:
            dataset_id = ele["submitter_id"]
            if dataset_id not in dataset_dict:
                dataset_dict[dataset_id] = ele
        return dataset_dict

    def get_pagination_count(self, display, restrict):
        count_display_result = self.generate_dataset_dictionary(display)
        count_restrict_result = self.generate_dataset_dictionary(restrict)
        id_list = list(count_display_result.keys())
        restrict_list = []
        for id in count_restrict_result.keys():
            if id not in count_display_result:
                id_list.append(id)
                restrict_list.append(id)
        return len(id_list), restrict_list

    def update_pagination_data(self, item, total, restrict, display):
        print(item)
        item.access.remove(Gen3Config.PUBLIC_ACCESS)
        display_result = self.generate_dataset_dictionary(display)

        items = []
        for id in display_result.keys():
            query_item = GraphQLQueryItem(node="experiment_query", filter={
                                          "submitter_id": [id]}, access=item.access)
            items.append((query_item, SUBMISSION, id))
        if total < item.page*item.limit:
            for ele in restrict:
                query_item = GraphQLQueryItem(node="experiment_query", filter={
                    "submitter_id": [ele]}, access=item.access)
            items.append((query_item, SUBMISSION, id))

        result_queue = queue.Queue()
        threads = []
        for args in items:
            t = threading.Thread(target=sgqlc.get_queried_result,
                                 args=(*args, result_queue))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        restrict_result = {}
        while not result_queue.empty():
            data = result_queue.get()
            restrict_result.update(data)

        for id in restrict_result.keys():
            if id in display_result.keys():
                display_result[id] = restrict_result[id][0]
        return list(display_result.values())

    def get_pagination_data(self, item):
        public_access = Gen3Config.PUBLIC_ACCESS
        display_item = GraphQLPaginationItem(
            limit=item.limit, page=item.page, filter=item.filter, access=[public_access])
        count_display_item = GraphQLPaginationItem(
            node="experiment_pagination_count", filter=item.filter, access=[public_access])
        private_access = copy.deepcopy(item.access)
        private_access.remove(public_access)
        count_restrict_item = GraphQLPaginationItem(
            node="experiment_pagination_count", filter=item.filter, access=private_access)

        items = [
            (display_item, SUBMISSION, "display"),
            (count_display_item, SUBMISSION, "count_display"),
            (count_restrict_item, SUBMISSION, "count_restrict")
        ]

        result_queue = queue.Queue()
        threads = []
        for args in items:
            t = threading.Thread(target=sgqlc.get_queried_result,
                                 args=(*args, result_queue))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        result = {}
        while not result_queue.empty():
            data = result_queue.get()
            result.update(data)

        return result

    def update_filter_values(self, filter, access):
        extra_filter = fg.generate_extra_filter(SUBMISSION, access)
        field = list(filter.keys())[0]
        value_list = []
        for ele_name in list(filter.values())[0]:
            for ele in FILTERS:
                if ele in extra_filter:
                    filter_dict = extra_filter
                else:
                    filter_dict = FILTERS
                # Check if ele can match with a exist filter object
                if filter_dict[ele]["field"] == field:
                    # Check if ele_name is a key under filter object element field
                    if ele_name in filter_dict[ele]["element"]:
                        ele_value = filter_dict[ele]["element"][ele_name]
                        if type(ele_value) == list:
                            value_list.extend(ele_value)
                        else:
                            value_list.append(ele_value)
                    else:
                        return filter
        return {field: value_list}

    def update_pagination_item(self, item, input, submission, SESSION):
        global SUBMISSION
        SUBMISSION = submission
        if item.filter != {}:
            filter_dict = {"submitter_id": []}
            temp_node_dict = {}
            for element in item.filter.values():
                filter_node = element["node"]
                filter_field = self.update_filter_values(
                    element["filter"], item.access)
                query_item = GraphQLQueryItem(
                    node=filter_node, filter=filter_field, access=item.access)
                filter_node = re.sub('_filter', '', filter_node)
                filter_field = list(filter_field.keys())[0]
                # Only do fetch when there is no related temp data stored in temp_node_dict
                # or the node field type is "String"
                if filter_node not in temp_node_dict or filter_field not in FIELDS:
                    query_result = sgqlc.get_queried_result(
                        query_item, SUBMISSION)
                    # The data will be stored when the field type is an "Array"
                    # The default filter relation of the Gen3 "Array" type field is "AND"
                    # We need "OR", therefore entire node data will go through a self-written filter function
                    if filter_field in FIELDS:
                        temp_node_dict[filter_node] = query_result[filter_node]
                elif filter_node in temp_node_dict and filter_field in FIELDS:
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

        if item.access == []:
            item.access.append(Gen3Config.PUBLIC_ACCESS)

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
        data = json.loads(re.sub("\'", '\"', cite))
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

    def handle_image_url(self, middle, filename, source_of, has_image):
        full_url = middle
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

    def update_manifests_based(self, uuid, middle, data, image=False):
        result = []
        for ele in data:
            item = {
                "image_url": self.handle_image_url(middle, ele["filename"], self.handle_empty_value(ele["is_source_of"]), image),
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

    def reconstruct_data_structure(self, data):
        result = []
        for ele in data:
            dataset_id = ele["submitter_id"]
            image_url_middle = f"/data/preview/{dataset_id}/"
            dataset_item = {
                "belong_to": ele["project_id"],
                "data_url_suffix": f"/data/browser/dataset/{dataset_id}?datasetTab=abstract",
                "source_url_middle": f"/data/download/{dataset_id}/",
                "contributors": self.update_contributors(ele["dataset_descriptions"][0]["contributor_name"]),
                "keywords": ele["dataset_descriptions"][0]["keywords"],
                "numberSamples": int(ele["dataset_descriptions"][0]["number_of_samples"][0]),
                "numberSubjects": int(ele["dataset_descriptions"][0]["number_of_subjects"][0]),
                "name": ele["dataset_descriptions"][0]["title"][0],
                "datasetId": dataset_id,
                "organs": ele["dataset_descriptions"][0]["study_organ_system"],
                "species": self.update_species(ele["cases"]),
                "plots": self.update_manifests_based(ele["id"], image_url_middle, ele["plots"]),
                "scaffoldViews": self.update_manifests_based(ele["id"], image_url_middle, ele["scaffoldViews"], True),
                "scaffolds": self.update_manifests_based(ele["id"], image_url_middle, ele["scaffolds"]),
                "thumbnails": self.update_manifests_based(ele["id"], image_url_middle, self.update_thumbnails(ele["thumbnails"]), True),
                "detailsReady": True,
            }
            result.append(dataset_item)
        return result
