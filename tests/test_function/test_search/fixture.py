import pytest

from app.data_schema import GraphQLPaginationItem
from app.function.search.search_logic import SearchLogic


@pytest.fixture
def sl_class():
    return SearchLogic(DummyESClass)


class DummyESClass:
    pass


@pytest.fixture
def dummy_search_data():
    return {
        "dummy dataset 1": 3,
        "dummy dataset 2": 1,
        "dummy dataset 3": 6,
        "dummy dataset 4": 2,
        "dummy dataset 5": 2,
    }


@pytest.fixture
def dummy_pagination_item():
    return GraphQLPaginationItem(node="experiment_pagination_count")
