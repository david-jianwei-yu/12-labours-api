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
    "MAPPED_FUNDING": {
        "title": "FUNDINGS",
        "node": "dataset_description",
        "field": "funding",
        "element": {
            "Funding A": ["OT3OD025349"],
            "Funding B": ["OT2OD023848"],
            "Funding C": ["OT2OD023847"]}
    },
    "MAPPED_MIME_TYPES2": {
        "title": "MIME TYPES2",
        "node": "manifest",
        "field": "additional_types",
        "element": {
            # "CSV": ["text/csv"],
            # "SEGMENTATION_FILES": ["application/vnd.mbfbioscience.metadata+xml", "application/vnd.mbfbioscience.neurolucida+xml"],
            # "CONTEXT_FILE": ["application/x.vnd.abi.context-information+json"],
            "Scaffold2": ["application/x.vnd.abi.scaffold.meta+json", "inode/vnd.abi.scaffold+file"],
            # "SCAFFOLD_VIEW_FILE": ["application/x.vnd.abi.scaffold.view+json", "inode/vnd.abi.scaffold.view+file"],
            # "SIMULATION_FILE": ["application/x.vnd.abi.simulation+json"],
            # "THUMBNAIL_IMAGE": ["image/x.vnd.abi.thumbnail+jpeg", "inode/vnd.abi.scaffold+thumbnail", "inode/vnd.abi.scaffold.thumbnail+file"],
            # "SCAFFOLD_DIR": ["inode/vnd.abi.scaffold+directory"],
            "Plot2": ["text/vnd.abi.plot+tab-separated-values", "text/vnd.abi.plot+csv"],
            # "COMMON_IMAGES": ["image/png", "image/jpeg"],
            # "tiff-image": ["image/tiff", "image/tif"],
            # "BIOLUCIDA_3D": ["image/jpx", "image/vnd.ome.xml+jpx"],
            # "BIOLUCIDA_2D": ["image/jp2", "image/vnd.ome.xml+jp2"],
            # "VIDEO": ["video/mp4"]
        }
    },
    "MAPPED_FUNDING2": {
        "title": "FUNDINGS2",
        "node": "dataset_description",
        "field": "funding",
        "element": {
            "Funding A2": ["OT3OD025349"],
            "Funding B2": ["OT2OD023848"],
            "Funding C2": ["OT2OD023847"]}
    }
}


class Filter:
    def or_relationship(self, item):
        # OR relationship
        if item.filter != {}:
            dataset_list = list(set(item.filter["submitter_id"]))
            item.filter["submitter_id"] = dataset_list

    def and_relationship(self, item):
        # AND relationship
        id_dict = {}
        dataset_list = []

        if item.filter != {}:
            # Create a id dict to count the frequency of occurrence
            for ele in item.filter["submitter_id"]:
                if ele not in id_dict.keys():
                    id_dict[ele] = 1
                else:
                    id_dict[ele] += 1
            # Find the matched id and add them into the dataset list
            for id in id_dict.keys():
                if id_dict[id] == max(id_dict.values()):
                    dataset_list.append(id)
            # Replace the filter id value
            item.filter["submitter_id"] = dataset_list

    def filter_relation(self, item):
        if item.relation == "and":
            self.and_relationship(item)
        elif item.relation == "or":
            self.or_relationship(item)

    def generate_dataset_list(self, data):
        dataset_list = [re.findall(
            "dataset-[0-9]*-version-[0-9]*", record["submitter_id"])[0] for record in data]
        return list(set(dataset_list))

    def generate_filter_information(self):
        filter_comp_info = {
            "size": len(FILTERS),
            "titles": [],
            "nodes": [],
            "fields": [],
            "elements": []
        }
        for ele in FILTERS:
            filter_comp_info["titles"].append(FILTERS[ele]["title"])
            filter_comp_info["nodes"].append(FILTERS[ele]["node"])
            filter_comp_info["fields"].append(FILTERS[ele]["field"])
            filter_comp_info["elements"].append(FILTERS[ele]["element"])
        return filter_comp_info
