from unittest.mock import MagicMock

from tests.test_function.test_filter.fixture import (
    DummyESClass,
    dummy_data_cache,
    dummy_data_cache_failure,
    dummy_data_cache_private,
    dummy_filter_cache,
    dummy_filter_cache_init,
    dummy_filter_cache_private,
    fg_class,
    fg_fe_class,
)


def test_generate_public_filter(
    fg_fe_class, fg_class, dummy_data_cache, dummy_filter_cache
):
    fg_class._handle_cache = MagicMock(return_value=dummy_data_cache)
    generate = fg_class.generate_public_filter()
    public_filter = fg_fe_class.cache_loader()
    assert generate is True
    assert public_filter == dummy_filter_cache


def test_generate_public_filter_failure(fg_class, dummy_data_cache_failure):
    fg_class._handle_cache = MagicMock(return_value=dummy_data_cache_failure)
    generate = fg_class.generate_public_filter()
    assert generate is False


def test_generate_private_filter(
    fg_class, dummy_data_cache, dummy_data_cache_private, dummy_filter_cache_private
):
    # Generate private filter requires public filter
    fg_class._handle_cache = MagicMock(return_value=dummy_data_cache)
    fg_class.generate_public_filter()
    fg_class._handle_cache = MagicMock(return_value=dummy_data_cache_private)
    private_filter = fg_class.generate_private_filter(["dummy access"])
    assert private_filter == dummy_filter_cache_private
