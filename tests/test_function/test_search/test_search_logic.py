from unittest.mock import MagicMock

from tests.test_function.test_search.fixture import (
    DummyESClass,
    dummy_pagination_item,
    dummy_search_data,
    sl_class,
)


def test_generate_searched_dataset(sl_class, dummy_search_data):
    sl_class._handle_searched_data = MagicMock(return_value=dummy_search_data)
    datasets = sl_class.generate_searched_dataset("dummy string input")
    assert datasets == {
        "submitter_id": [
            "dummy dataset 3",
            "dummy dataset 1",
            "dummy dataset 4",
            "dummy dataset 5",
            "dummy dataset 2",
        ]
    }


def test_implement_search_filter_relation(
    sl_class, dummy_pagination_item, dummy_search_data
):
    sl_class._handle_searched_data = MagicMock(return_value=dummy_search_data)
    dummy_pagination_item.search = sl_class.generate_searched_dataset(
        "dummy string input"
    )
    dummy_pagination_item.filter = {
        "submitter_id": [
            "dummy dataset 2",
            "dummy dataset 4",
            "dummy dataset 5",
        ]
    }
    relation = sl_class.implement_search_filter_relation(dummy_pagination_item)
    assert relation == [
        "dummy dataset 4",
        "dummy dataset 5",
        "dummy dataset 2",
    ]


def test_implement_search_filter_relation_no_match(
    sl_class, dummy_pagination_item, dummy_search_data
):
    sl_class._handle_searched_data = MagicMock(return_value=dummy_search_data)
    dummy_pagination_item.search = sl_class.generate_searched_dataset(
        "dummy string input"
    )
    dummy_pagination_item.filter = {
        "submitter_id": [
            "dummy dataset 6",
        ]
    }
    relation = sl_class.implement_search_filter_relation(dummy_pagination_item)
    assert relation == []


def test_implement_search_filter_relation_no_filter(
    sl_class, dummy_pagination_item, dummy_search_data
):
    sl_class._handle_searched_data = MagicMock(return_value=dummy_search_data)
    dummy_pagination_item.search = sl_class.generate_searched_dataset(
        "dummy string input"
    )
    dummy_pagination_item.filter = {"submitter_id": []}
    relation = sl_class.implement_search_filter_relation(dummy_pagination_item)
    assert relation == []
