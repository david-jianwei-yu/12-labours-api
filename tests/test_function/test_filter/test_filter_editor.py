import pytest

from app.function.filter.filter_editor import FilterEditor
from tests.test_function.test_filter.fixture import dummy_filter_cache, filter_template


@pytest.fixture
def dummy_filter():
    return dummy_filter_cache()


@pytest.fixture
def fe_class():
    return FilterEditor()


def test_cache_loader(fe_class):
    template = fe_class.cache_loader()
    assert template == filter_template()


def test_update_filter_cache(fe_class, dummy_filter):
    fe_class.update_filter_cache(dummy_filter)
    cache = fe_class.cache_loader()
    assert cache == dummy_filter
