class DummyESClass:
    pass


def filter_template():
    return {
        "MAPPED_ADDITIONAL_TYPES": {
            "facets": {
                "Dicom": "application/dicom",
                "Plot": [
                    "text/vnd.abi.plot+tab-separated-values",
                    "text/vnd.abi.plot+csv",
                ],
                "Scaffold": "application/x.vnd.abi.scaffold.meta+json",
            },
            "field": "additional_types",
            "node": "manifest_filter",
            "title": "data type",
        },
        "MAPPED_AGE_CATEGORY": {
            "facets": {},
            "field": "age_category",
            "node": "case_filter",
            "title": "age category",
        },
        "MAPPED_PROJECT_ID": {
            "facets": {},
            "field": "project_id",
            "node": "experiment_filter",
            "title": "access scope",
        },
        "MAPPED_SEX": {
            "facets": {"Female": ["F", "Female"], "Male": ["M", "Male"]},
            "field": "sex",
            "node": "case_filter",
            "title": "sex",
        },
        "MAPPED_SPECIES": {
            "facets": {
                "Cat": "Felis catus",
                "Human": "Homo sapiens",
                "Mouse": "Mus musculus",
                "Pig": "Sus scrofa",
                "Rat": "Rattus norvegicus",
            },
            "field": "species",
            "node": "case_filter",
            "title": "species",
        },
        "MAPPED_STUDY_ORGAN_SYSTEM": {
            "facets": {},
            "field": "study_organ_system",
            "node": "dataset_description_filter",
            "title": "anatomical structure",
        },
    }


def dummy_filter_cache_empty():
    return {
        "MAPPED_AGE_CATEGORY": {
            "facets": {},
            "field": "age_category",
            "node": "case_filter",
            "title": "age category",
        },
        "MAPPED_PROJECT_ID": {
            "facets": {},
            "field": "project_id",
            "node": "experiment_filter",
            "title": "access scope",
        },
        "MAPPED_STUDY_ORGAN_SYSTEM": {
            "facets": {},
            "field": "study_organ_system",
            "node": "dataset_description_filter",
            "title": "anatomical structure",
        },
    }


def dummy_filter_cache():
    return {
        "MAPPED_AGE_CATEGORY": {
            "facets": {"Dummy age category": "dummy age category"},
            "field": "age_category",
            "node": "case_filter",
            "title": "age category",
        },
        "MAPPED_PROJECT_ID": {
            "facets": {"Dummy project": "dummy project"},
            "field": "project_id",
            "node": "experiment_filter",
            "title": "access scope",
        },
        "MAPPED_STUDY_ORGAN_SYSTEM": {
            "facets": {"Dummy organ": "dummy organ"},
            "field": "study_organ_system",
            "node": "dataset_description_filter",
            "title": "anatomical structure",
        },
    }


def dummy_filter_cache_private():
    return {
        "MAPPED_AGE_CATEGORY": {
            "facets": {"Dummy age category": "dummy age category"},
            "field": "age_category",
            "node": "case_filter",
            "title": "age category",
        },
        "MAPPED_PROJECT_ID": {
            "facets": {
                "Dummy project": "dummy project",
                "Dummy private project": "dummy private project",
            },
            "field": "project_id",
            "node": "experiment_filter",
            "title": "access scope",
        },
        "MAPPED_STUDY_ORGAN_SYSTEM": {
            "facets": {"Dummy organ": "dummy organ"},
            "field": "study_organ_system",
            "node": "dataset_description_filter",
            "title": "anatomical structure",
        },
    }


def dummy_cache():
    return {
        "case_filter": [
            {
                "age_category": "dummy age category",
                "experiments": [
                    {
                        "id": "dummy uuid",
                        "project_id": "dummy project",
                        "submitter_id": "dummy submitter",
                    }
                ],
                "id": "dummy uuid",
                "sex": "dummy sex",
                "species": "dummy species",
            }
        ],
        "dataset_description_filter": [
            {
                "experiments": [
                    {
                        "id": "dummy uuid",
                        "project_id": "dummy project",
                        "submitter_id": "dummy submitter",
                    }
                ],
                "id": "dummy uuid",
                "keywords": ["dummy keywords"],
                "study_organ_system": ["dummy organ"],
            }
        ],
        "experiment_filter": [
            {
                "id": "dummy uuid",
                "project_id": "dummy project",
                "submitter_id": "dummy submitter",
            }
        ],
    }


def dummy_cache_failure():
    return {
        "case_filter": [],
        "dataset_description_filter": [],
        "experiment_filter": [],
    }
