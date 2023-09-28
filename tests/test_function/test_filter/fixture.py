import pytest

from app.data_schema import GraphQLPaginationItem
from app.function.filter.filter_editor import FilterEditor
from app.function.filter.filter_formatter import FilterFormatter
from app.function.filter.filter_generator import FilterGenerator
from app.function.filter.filter_logic import FilterLogic


@pytest.fixture
def fe_class():
    return FilterEditor()


@pytest.fixture
def ff_class(dummy_filter_cache):
    fe = FilterEditor()
    fe.update_filter_cache(dummy_filter_cache)
    return FilterFormatter(fe)


@pytest.fixture
def fg_fe_class(dummy_filter_cache_init):
    fe = FilterEditor()
    fe.update_filter_cache(dummy_filter_cache_init)
    return fe


@pytest.fixture
def fg_class(fg_fe_class):
    return FilterGenerator(fg_fe_class, DummyESClass)


@pytest.fixture
def fl_class():
    return FilterLogic()


class DummyESClass:
    pass


@pytest.fixture
def filter_template():
    return {
        "MAPPED_ADDITIONAL_TYPES": {
            "title": "data type",
            "node": "manifest_filter",
            "field": "additional_types",
            "facets": {
                "Dicom": "application/dicom",
                "Plot": [
                    "text/vnd.abi.plot+tab-separated-values",
                    "text/vnd.abi.plot+csv",
                ],
                "Scaffold": "application/x.vnd.abi.scaffold.meta+json",
            },
        },
        "MAPPED_AGE_CATEGORY": {
            "title": "age category",
            "node": "case_filter",
            "field": "age_category",
            "facets": {},
        },
        "MAPPED_PROJECT_ID": {
            "title": "access scope",
            "node": "experiment_filter",
            "field": "project_id",
            "facets": {},
        },
        "MAPPED_SEX": {
            "title": "sex",
            "node": "case_filter",
            "field": "sex",
            "facets": {"Female": ["F", "Female"], "Male": ["M", "Male"]},
        },
        "MAPPED_SPECIES": {
            "title": "species",
            "node": "case_filter",
            "field": "species",
            "facets": {
                "Cat": "Felis catus",
                "Human": "Homo sapiens",
                "Mouse": "Mus musculus",
                "Pig": "Sus scrofa",
                "Rat": "Rattus norvegicus",
            },
        },
        "MAPPED_STUDY_ORGAN_SYSTEM": {
            "title": "anatomical structure",
            "node": "dataset_description_filter",
            "field": "study_organ_system",
            "facets": {},
        },
    }


@pytest.fixture
def dummy_filter_cache_init():
    return {
        "MAPPED_AGE_CATEGORY": {
            "title": "Age category",
            "node": "case_filter",
            "field": "age_category",
            "facets": {},
        },
        "MAPPED_PROJECT_ID": {
            "title": "Access scope",
            "node": "experiment_filter",
            "field": "project_id",
            "facets": {},
        },
        "MAPPED_STUDY_ORGAN_SYSTEM": {
            "title": "Anatomical structure",
            "node": "dataset_description_filter",
            "field": "study_organ_system",
            "facets": {},
        },
    }


@pytest.fixture
def dummy_filter_cache():
    return {
        "MAPPED_AGE_CATEGORY": {
            "title": "Age category",
            "node": "case_filter",
            "field": "age_category",
            "facets": {"Dummy age category": "dummy age category"},
        },
        "MAPPED_PROJECT_ID": {
            "title": "Access scope",
            "node": "experiment_filter",
            "field": "project_id",
            "facets": {"Dummy project": "dummy project"},
        },
        "MAPPED_STUDY_ORGAN_SYSTEM": {
            "title": "Anatomical structure",
            "node": "dataset_description_filter",
            "field": "study_organ_system",
            "facets": {"Dummy organ": "dummy organ"},
        },
    }


@pytest.fixture
def dummy_filter_cache_private():
    return {
        "MAPPED_PROJECT_ID": {
            "title": "Access scope",
            "node": "experiment_filter",
            "field": "project_id",
            "facets": {
                "Dummy private project": "dummy private project",
                "Dummy project": "dummy project",
            },
        },
    }


@pytest.fixture
def dummy_data_cache():
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


@pytest.fixture
def dummy_data_cache_private():
    return {
        "case_filter": [],
        "dataset_description_filter": [],
        "experiment_filter": [
            {
                "id": "dummy uuid",
                "project_id": "dummy private project",
                "submitter_id": "dummy submitter",
            },
        ],
    }


@pytest.fixture
def dummy_data_cache_failure():
    return {
        "case_filter": [],
        "dataset_description_filter": [],
        "experiment_filter": [],
    }


@pytest.fixture
def dummy_filter_data():
    return {
        '{"project_id": ["dummy project"]}': [
            {
                "id": "dummy id",
                "project_id": "dummy project",
                "submitter_id": "dummy dataset 1",
            },
            {
                "id": "dummy id",
                "project_id": "dummy project",
                "submitter_id": "dummy dataset 2",
            },
            {
                "id": "dummy id",
                "project_id": "dummy project",
                "submitter_id": "dummy dataset 3",
            },
        ],
        '{"additional_types": ["dummy type"]}': [
            {
                "additional_types": "dummy type",
                "experiments": [
                    {
                        "id": "dummy id",
                        "project_id": "dummy project",
                        "submitter_id": "dummy dataset 2",
                    }
                ],
                "id": "dummy id",
            },
            {
                "additional_types": "dummy type",
                "experiments": [
                    {
                        "id": "dummy id",
                        "project_id": "dummy project",
                        "submitter_id": "dummy dataset 3",
                    }
                ],
                "id": "dummy id",
            },
            {
                "additional_types": "dummy type",
                "experiments": [
                    {
                        "id": "dummy id",
                        "project_id": "dummy project",
                        "submitter_id": "dummy dataset 4",
                    }
                ],
                "id": "dummy id",
            },
        ],
    }


@pytest.fixture
def dummy_filter_item():
    return GraphQLPaginationItem(node="experiment_pagination_count")
