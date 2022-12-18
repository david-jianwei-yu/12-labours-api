import re

BAD_REQUEST = 400
UNAUTHORIZED = 401
NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405
INTERNAL_SERVER_ERROR = 500

FILTERS = {
    "MAPPED_MIME_TYPES": {
        "title": "MIME TYPES",
        "node": "manifest",
        "field": "additional_types",
        "element": {
            # "CSV": ["text/csv"],
            # "SEGMENTATION_FILES": ["application/vnd.mbfbioscience.metadata+xml", "application/vnd.mbfbioscience.neurolucida+xml"],
            # "CONTEXT_FILE": ["application/x.vnd.abi.context-information+json"],
            "Scaffold": ["application/x.vnd.abi.scaffold.meta+json", "inode/vnd.abi.scaffold+file"],
            # "SCAFFOLD_VIEW_FILE": ["application/x.vnd.abi.scaffold.view+json", "inode/vnd.abi.scaffold.view+file"],
            # "SIMULATION_FILE": ["application/x.vnd.abi.simulation+json"],
            # "THUMBNAIL_IMAGE": ["image/x.vnd.abi.thumbnail+jpeg", "inode/vnd.abi.scaffold+thumbnail", "inode/vnd.abi.scaffold.thumbnail+file"],
            # "SCAFFOLD_DIR": ["inode/vnd.abi.scaffold+directory"],
            "Plot": ["text/vnd.abi.plot+tab-separated-values", "text/vnd.abi.plot+csv"],
            # "COMMON_IMAGES": ["image/png", "image/jpeg"],
            # "tiff-image": ["image/tiff", "image/tif"],
            # "BIOLUCIDA_3D": ["image/jpx", "image/vnd.ome.xml+jpx"],
            # "BIOLUCIDA_2D": ["image/jp2", "image/vnd.ome.xml+jp2"],
            # "VIDEO": ["video/mp4"]
        }
    },
    "MAPPED_ANATOMICAL_STRUCTURE": {
        "title": "ANATOMICAL STRUCTURE",
        "node": "dataset_description",
        "field": "keywords",
        "element": {
            "Bladder": "bladder",
            "Brainstem": "brainstem",
            "Colon": "colon",
            "Heart": "heart",
            "Lungs": "lungs",
            "Spinal Cord": "spinal cord",
            "Stomach": "stomach",
        }
    },
    "MAPPED_SPECIES": {
        "title": "SPECIES",
        "node": "dataset_description",
        "field": "keywords",
        "element": {
            "Human": "human",
            "Rat": "rat",
            "Mouse": "mouse",
            "Pig": "pig",
            "Sheep": "sheep"
        }
    }
}


# This list contains all the "Array" type fields that used as a filter
FIELDS = ["keywords", "study_organ_system"]


class Filter:
    def generate_filtered_datasets(self, filter, field, data):
        result = []
        for element in data:
            word_list = [value for value in element[field]]
            for kwd in filter[field]:
                if kwd in word_list:
                    result.append(element)
        return result

    def get_filtered_datasets(self, filter, data):
        field = list(filter.keys())[0]
        if field in FIELDS:
            data = self.generate_filtered_datasets(filter, field, data)
        dataset_list = set()
        for record in data:
            dataset_list.add(re.findall(
                "dataset-[0-9]*-version-[0-9]*", record["submitter_id"])[0])
        return list(dataset_list)

    def filter_relation(self, item):
        nested_list = item.filter["submitter_id"]
        if item.relation == "and":  # AND relationship
            dataset_list = set(nested_list[0]).intersection(*nested_list)
        elif item.relation == "or":  # OR relationship
            dataset_list = set()
            for sublist in nested_list:
                for id in sublist:
                    dataset_list.add(id)
        item.filter["submitter_id"] = list(dataset_list)

    def generate_filter_information(self):
        filter_information = {
            "size": len(FILTERS),
            "titles": [],
            "nodes": [],
            "fields": [],
            "elements": [],
            "ids": []
        }
        for element in FILTERS:
            filter_information["titles"].append(FILTERS[element]["title"])
            filter_information["nodes"].append(FILTERS[element]["node"])
            filter_information["fields"].append(FILTERS[element]["field"])
            filter_information["elements"].append(FILTERS[element]["element"])
            for ele in FILTERS[element]["element"]:
                filter_information["ids"].append(ele)
        return filter_information
