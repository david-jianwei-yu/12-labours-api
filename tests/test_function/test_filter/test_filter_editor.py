import pytest

from app.function.filter.filter_editor import FilterEditor


@pytest.fixture
def fe_class():
    return FilterEditor()


@pytest.fixture
def dummy_filter():
    return {
        "MAPPED_DUMMY_FILTER": {
            "facets": {
                "dummy_facet1": "dummy_value1",
                "dummy_facet2": ["dummy_value2"],
            },
            "field": "dummy_field",
            "node": "dummy_node",
            "title": "dummy_title",
        }
    }


def test_cache_loader(fe_class):
    template = fe_class.cache_loader()
    assert template == {
        "MAPPED_ADDITIONAL_TYPES": {
            "facets": {
                "Dicom": ["application/dicom"],
                "Plot": [
                    "text/vnd.abi.plot+tab-separated-values",
                    "text/vnd.abi.plot+csv",
                ],
                "Scaffold": [
                    "application/x.vnd.abi.scaffold.meta+json",
                    "inode/vnd.abi.scaffold+file",
                ],
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


def test_update_filter_cache(fe_class, dummy_filter):
    fe_class.update_filter_cache(dummy_filter)
    cache = fe_class.cache_loader()
    assert cache == dummy_filter
