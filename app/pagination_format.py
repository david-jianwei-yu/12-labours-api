import re
import json


class PaginationFormat(object):
    def __init__(self, fg):
        self.FILTER_MAP = fg.get_filter_map()

    def update_thumbnail(self, data):
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
        data = json.loads(re.sub('\'', '\"', cite))
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

    def handle_empty_value(self, data):
        if data == None or data == "NA":
            return ""
        return data

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

    def update_manifest_based(self, uuid, middle, data, image=False):
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

    def update_species(self, data):
        result = []
        if data == []:
            return result
        for ele in data:
            if ele["species"] != "NA":
                species_filter = self.FILTER_MAP["MAPPED_SPECIES"]["facets"]
                species = list(species_filter.keys())[list(
                    species_filter.values()).index(ele["species"])]
                if species not in result:
                    result.append(species)
        return result

    def update_contributor(self, data):
        result = []
        if data == []:
            return result
        for ele in data:
            contributor = {
                "name": ele
            }
            result.append(contributor)
        return result

    def reconstruct_data_structure(self, data):
        result = []
        for ele in data:
            dataset_id = ele["submitter_id"]
            image_url_middle = f"/data/preview/{dataset_id}/"
            dataset_item = {
                "data_url_suffix": f"/data/browser/dataset/{dataset_id}?datasetTab=abstract",
                "source_url_middle": f"/data/download/{dataset_id}/",
                "contributors": self.update_contributor(ele["dataset_descriptions"][0]["contributor_name"]),
                "keywords": ele["dataset_descriptions"][0]["keywords"],
                "numberSamples": int(ele["dataset_descriptions"][0]["number_of_samples"][0]),
                "numberSubjects": int(ele["dataset_descriptions"][0]["number_of_subjects"][0]),
                "name": ele["dataset_descriptions"][0]["title"][0],
                "datasetId": dataset_id,
                "organs": ele["dataset_descriptions"][0]["study_organ_system"],
                "species": self.update_species(ele["cases"]),
                "plots": self.update_manifest_based(ele["id"], image_url_middle, ele["plots"]),
                "scaffoldViews": self.update_manifest_based(ele["id"], image_url_middle, ele["scaffoldViews"], True),
                "scaffolds": self.update_manifest_based(ele["id"], image_url_middle, ele["scaffolds"]),
                "thumbnails": self.update_manifest_based(ele["id"], image_url_middle, self.update_thumbnail(ele["thumbnails"]), True),
                "mris": self.update_manifest_based(ele["id"], image_url_middle, ele["mris"]),
                "dicomImages": self.update_manifest_based(ele["id"], image_url_middle, ele["dicomImages"]),
                "detailsReady": True,
            }
            result.append(dataset_item)
        return result
