FILTERS = {
    "MAPPED_AGE_CATEGORY": {
        "title": "AGE CATEGORY",
        "node": "case_filter",
        "field": "age_category",
        "element": {
            "Adolescent": "Adolescent",
            "Adult": "prime adult stage",
            "Juvenile": "Juvenile",
        }
    },
    "MAPPED_ANATOMICAL_STRUCTURE": {
        "title": "ANATOMICAL STRUCTURE",
        "node": "dataset_description_filter",
        "field": "study_organ_system",
        "element": {
            "Body Proper": "body proper",
            "Brainstem": "brainstem",
            "Cardiac Nerve Plexus": "cardiac nerve plexus",
            "Colon": "colon",
            "Heart": "heart",
            "Lungs": "lungs",
            # "Myenteric Nerve Plexus": "myenteric nerve plexus",
            "Spinal Cord": "spinal cord",
            "Stomach": "stomach",
            "Urinary Bladder": "urinary bladder",
            "Vagus Nerve": "vagus nerve",
        }
    },
    "MAPPED_SEX": {
        "title": "SEX",
        "node": "case_filter",
        "field": "sex",
        "element": {
            "Female": "Female",
            "Male": "Male",
        }
    },
    "MAPPED_MIME_TYPE": {
        "title": "MIME TYPE",
        "node": "manifest_filter",
        "field": "additional_types",
        "element": {
            "Plot": ["text/vnd.abi.plot+tab-separated-values", "text/vnd.abi.plot+csv"],
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
        "title": "SPECIES",
        "node": "case_filter",
        "field": "species",
        "element": {
            "Cat": "Felis catus",
            "Human": "Homo sapiens",
            "Mouse": "Mus musculus",
            "Pig": "Sus scrofa",
            "Rat": "Rattus norvegicus",
        }
    }
}
