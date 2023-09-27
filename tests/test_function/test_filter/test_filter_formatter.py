import pytest

from app.function.filter.filter_editor import FilterEditor
from app.function.filter.filter_formatter import FilterFormatter


@pytest.fixture
def dummy_filter():
    return {
        "MAPPED_DUMMY_FILTER": {
            "facets": {
                "Dummy_facet1": "dummy_value1",
                "Dummy_facet2": ["dummy_value2"],
            },
            "field": "dummy_field",
            "node": "dummy_node",
            "title": "dummy_title",
        }
    }


@pytest.fixture
def fe_class(dummy_filter):
    fe = FilterEditor()
    fe.update_filter_cache(dummy_filter)
    return fe


@pytest.fixture
def ff_class(fe_class):
    return FilterFormatter(fe_class)


@pytest.fixture
def dummy_private_filter(dummy_filter):
    private_filter = dummy_filter["MAPPED_DUMMY_FILTER"]["facets"][
        "Dummy_private_facet"
    ] = "dummy_private_value"
    return private_filter


def test_generate_sidebar_filter_format(ff_class, dummy_private_filter):
    sidebar_format = ff_class.generate_sidebar_filter_format(dummy_private_filter)
    assert sidebar_format == [
        {
            "key": "dummy_node>dummy_field",
            "label": "Dummy_title",
            "children": [
                {"facetPropPath": "dummy_node>dummy_field", "label": "Dummy_facet1"},
                {"facetPropPath": "dummy_node>dummy_field", "label": "Dummy_facet2"},
                {
                    "facetPropPath": "dummy_node>dummy_field",
                    "label": "Dummy_private_facet",
                },
            ],
        }
    ]


def test_generate_filter_format(ff_class, dummy_private_filter):
    format_ = ff_class.generate_filter_format(dummy_private_filter)
    assert format_ == {
        "size": 1,
        "titles": ["Dummy_title"],
        "nodes>fields": ["dummy_node>dummy_field"],
        "elements": [["Dummy_facet1", "Dummy_facet2", "Dummy_private_facet"]],
    }
