import re

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


class Filter:
    def filter_relation(self, item):
        filter_list = []
        for sublist in item.filter["submitter_id"]:
            if sublist != [] and sublist != None:
                filter_list.append(sublist)
        item.filter["submitter_id"] = filter_list

        if item.relation == "and":  # AND relationship
            nested_list = item.filter["submitter_id"]
            dataset_list = list(set(nested_list[0]).intersection(*nested_list))
            item.filter["submitter_id"] = dataset_list
        elif item.relation == "or":  # OR relationship
            flatten_list = []
            for sublist in item.filter["submitter_id"]:
                for ele in sublist:
                    flatten_list.append(ele)
            dataset_list = list(set(flatten_list))
            item.filter["submitter_id"] = dataset_list

    def generate_keywords_filed_filter(self, filter, data):
        result = []
        for ele in data:
            keyword_list = [item.strip() for item in ele["keywords"]]
            for kwd in filter["keywords"]:
                if any(kwd in word for word in keyword_list):
                    result.append(ele)
        return result

    def generate_dataset_list(self, filter, data):
        if "keywords" in filter:
            data = self.generate_keywords_filed_filter(filter, data)
        dataset_list = [re.findall(
            "dataset-[0-9]*-version-[0-9]*", record["submitter_id"])[0] for record in data]
        return list(set(dataset_list))

    def generate_filter_information(self):
        filter_comp_info = {
            "size": len(FILTERS),
            "titles": [],
            "nodes": [],
            "fields": [],
            "elements": [],
            "ids": []
        }
        for element in FILTERS:
            filter_comp_info["titles"].append(FILTERS[element]["title"])
            filter_comp_info["nodes"].append(FILTERS[element]["node"])
            filter_comp_info["fields"].append(FILTERS[element]["field"])
            filter_comp_info["elements"].append(FILTERS[element]["element"])
            for ele in FILTERS[element]["element"]:
                filter_comp_info["ids"].append(ele)
        return filter_comp_info
