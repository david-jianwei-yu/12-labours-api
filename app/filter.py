import re

MAPPED_MIME_TYPES = {
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

MAPPED_FUNDING = {
    "Funding A": ["OT3OD025349"],
    "Funding B": ["OT2OD023848"]
}


class Filter:
    def or_relationship(self, item):
        pass

    def and_relationship(self, item):
        # AND relationship
        count_filter = 0
        id_dict = {}
        filter_dict = {"submitter_id": []}

        if item.filter != {}:
            # Create a id dict to count the frequency of occurrence
            for key in item.filter.keys():
                count_filter += 1
                for ele in item.filter[key]:
                    if ele not in id_dict.keys():
                        id_dict[ele] = 1
                    else:
                        id_dict[ele] += 1
            # Find the matched id and add them into the dict with key submitter_id
            for id in id_dict.keys():
                if id_dict[id] == max(id_dict.values()):
                    filter_dict["submitter_id"].append(id)
            # Replace the filter with created dict
            item.filter = filter_dict

    def filter_relation(self, item, relation):
        if relation == "and":
            self.and_relationship(self, item)
        elif relation == "or":
            self.or_relationship(self, item)

    def generate_dataset_info_list(self, data):
        dataset_list = [re.findall(
            "dataset-[0-9]*-version-[0-9]*", record["submitter_id"])[0] for record in data]
        return list(set(dataset_list))

    def generate_filter_data(self):
        filter_component_info = {
            "title": ["DATA TYPES", "FUNDING", "TEST TITLE 1", "TEST TITLE 2"],
            "node": ["manifest", "dataset_description", "test node 1", "test node 2"],
            "field": ["additional_types", "funding", "test 1", "test 2"],
            "element": {
                "additional_types": MAPPED_MIME_TYPES, "funding": MAPPED_FUNDING, "test 1": MAPPED_MIME_TYPES, "test 2": MAPPED_FUNDING
            }
        }
        return filter_component_info
