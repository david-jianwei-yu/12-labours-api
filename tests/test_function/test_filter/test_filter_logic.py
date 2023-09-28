from tests.test_function.test_filter.fixture import (
    dummy_filter_data,
    dummy_filter_item,
    fl_class,
)


def test_generate_filtered_dataset(fl_class, dummy_filter_data):
    datasets = fl_class.generate_filtered_dataset(dummy_filter_data)
    assert datasets == {
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


def test_implement_filter_relation_and(fl_class, dummy_filter_data, dummy_filter_item):
    dummy_filter_item.filter = fl_class.generate_filtered_dataset(dummy_filter_data)
    dummy_filter_item.relation = "and"
    and_relation = fl_class.implement_filter_relation(dummy_filter_item)
    assert and_relation == [
        "dummy dataset 2",
        "dummy dataset 3",
    ]


def test_implement_filter_relation_or(
    fl_class,
    dummy_filter_data,
    dummy_filter_item,
):
    dummy_filter_item.filter = fl_class.generate_filtered_dataset(dummy_filter_data)
    dummy_filter_item.relation = "or"
    or_relation = fl_class.implement_filter_relation(dummy_filter_item)
    assert or_relation == [
        "dummy dataset 1",
        "dummy dataset 2",
        "dummy dataset 3",
        "dummy dataset 4",
    ]
