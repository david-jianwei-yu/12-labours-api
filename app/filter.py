import re

MAPPED_MIME_TYPES = {
    # "CSV": ["text/csv"],
    # "SEGMENTATION_FILES": ["application/vnd.mbfbioscience.metadata+xml", "application/vnd.mbfbioscience.neurolucida+xml"],
    # "CONTEXT_FILE": ["application/x.vnd.abi.context-information+json"],
    "SCAFFOLD_FILE": ["application/x.vnd.abi.scaffold.meta+json", "inode/vnd.abi.scaffold+file"],
    # "SCAFFOLD_VIEW_FILE": ["application/x.vnd.abi.scaffold.view+json", "inode/vnd.abi.scaffold.view+file"],
    # "SIMULATION_FILE": ["application/x.vnd.abi.simulation+json"],
    # "THUMBNAIL_IMAGE": ["image/x.vnd.abi.thumbnail+jpeg", "inode/vnd.abi.scaffold+thumbnail", "inode/vnd.abi.scaffold.thumbnail+file"],
    # "SCAFFOLD_DIR": ["inode/vnd.abi.scaffold+directory"],
    "PLOT_FILE": ["text/vnd.abi.plot+tab-separated-values", "text/vnd.abi.plot+csv"],
    # "COMMON_IMAGES": ["image/png", "image/jpeg"],
    # "tiff-image": ["image/tiff", "image/tif"],
    # "BIOLUCIDA_3D": ["image/jpx", "image/vnd.ome.xml+jpx"],
    # "BIOLUCIDA_2D": ["image/jp2", "image/vnd.ome.xml+jp2"],
    # "VIDEO": ["video/mp4"]
}


class Filter:
    def generate_dataset_info_list(self, data):
        dataset_list = [re.findall(
            "dataset-[0-9]*-version-[0-9]*", record["submitter_id"])[0] for record in data]
        return list(set(dataset_list))

    def generate_filter_data(self):
        return {
            "DATA TYPES": MAPPED_MIME_TYPES
        }
