from tests.test_function.test_filter.fixture import (
    dummy_filter_cache,
    fe_class,
    filter_template,
)


def test_cache_loader(fe_class, filter_template):
    template = fe_class.cache_loader()
    assert template == filter_template


def test_update_filter_cache(fe_class, dummy_filter_cache):
    fe_class.update_filter_cache(dummy_filter_cache)
    cache = fe_class.cache_loader()
    assert cache == dummy_filter_cache
