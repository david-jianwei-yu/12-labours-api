import pytest

from app.function.filter.filter_editor import FilterEditor
from app.function.filter.filter_formatter import FilterFormatter
from tests.test_function.test_filter.fixture import (
    dummy_filter_cache,
    dummy_filter_cache_private,
)


@pytest.fixture
def ff_class():
    fe = FilterEditor()
    fe.update_filter_cache(dummy_filter_cache())
    return FilterFormatter(fe)


@pytest.fixture
def dummy_private_filter():
    return dummy_filter_cache_private()


def test_generate_sidebar_filter_format(ff_class, dummy_private_filter):
    sidebar_format = ff_class.generate_sidebar_filter_format(dummy_private_filter)
    assert sidebar_format == [
        {
            "key": "case_filter>age_category",
            "label": "Age category",
            "children": [
                {
                    "facetPropPath": "case_filter>age_category",
                    "label": "Dummy age category",
                }
            ],
        },
        {
            "key": "experiment_filter>project_id",
            "label": "Access scope",
            "children": [
                {
                    "facetPropPath": "experiment_filter>project_id",
                    "label": "Dummy private project",
                },
                {
                    "facetPropPath": "experiment_filter>project_id",
                    "label": "Dummy project",
                },
            ],
        },
        {
            "key": "dataset_description_filter>study_organ_system",
            "label": "Anatomical structure",
            "children": [
                {
                    "facetPropPath": "dataset_description_filter>study_organ_system",
                    "label": "Dummy organ",
                }
            ],
        },
    ]


def test_generate_filter_format(ff_class, dummy_private_filter):
    format_ = ff_class.generate_filter_format(dummy_private_filter)
    assert format_ == {
        "size": 3,
        "titles": ["Age category", "Access scope", "Anatomical structure"],
        "nodes>fields": [
            "case_filter>age_category",
            "experiment_filter>project_id",
            "dataset_description_filter>study_organ_system",
        ],
        "elements": [
            ["Dummy age category"],
            ["Dummy private project", "Dummy project"],
            ["Dummy organ"],
        ],
    }
