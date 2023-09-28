import pytest

from app.function.filter.filter_logic import FilterLogic
from tests.test_function.test_filter.fixture import dummy_filter_data, dummy_filter_item


@pytest.fixture
def dummy_data():
    return dummy_filter_data()


@pytest.fixture
def dummy_item():
    return dummy_filter_item()


@pytest.fixture
def fl_class():
    return FilterLogic()


def test_generate_filtered_dataset(dummy_data, fl_class):
    assert fl_class.generate_filtered_dataset(dummy_data) == {
        "submitter_id": [
            [
                "dummy dataset 1",
                "dummy dataset 2",
                "dummy dataset 3",
            ],
            [
                "dummy dataset 2",
                "dummy dataset 3",
                "dummy dataset 4",
            ],
        ]
    }


def test_implement_filter_relation_and(dummy_data, dummy_item, fl_class):
    dummy_item.filter = fl_class.generate_filtered_dataset(dummy_data)
    dummy_item.relation = "and"
    assert fl_class.implement_filter_relation(dummy_item) == [
        "dummy dataset 2",
        "dummy dataset 3",
    ]


def test_implement_filter_relation_or(dummy_data, dummy_item, fl_class):
    dummy_item.filter = fl_class.generate_filtered_dataset(dummy_data)
    dummy_item.relation = "or"
    assert fl_class.implement_filter_relation(dummy_item) == [
        "dummy dataset 1",
        "dummy dataset 2",
        "dummy dataset 3",
        "dummy dataset 4",
    ]
