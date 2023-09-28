from unittest.mock import MagicMock

import pytest

from app.function.filter.filter_editor import FilterEditor
from app.function.filter.filter_generator import FilterGenerator

# from services.external_service import ExternalService
from tests.test_function.test_filter.fixture import (
    DummyESClass,
    dummy_cache,
    dummy_cache_failure,
    dummy_cache_private,
    dummy_filter_cache,
    dummy_filter_cache_init,
    dummy_filter_cache_private,
)


@pytest.fixture
def fe_class():
    fe = FilterEditor()
    fe.update_filter_cache(dummy_filter_cache_init())
    return fe


@pytest.fixture
def fg_class(fe_class):
    return FilterGenerator(fe_class, DummyESClass)


def test_generate_public_filter(fe_class, fg_class):
    fg_class._handle_cache = MagicMock(return_value=dummy_cache())
    assert fg_class.generate_public_filter() == True
    assert fe_class.cache_loader() == dummy_filter_cache()


def test_generate_public_filter_failure(fg_class):
    fg_class._handle_cache = MagicMock(return_value=dummy_cache_failure())
    assert fg_class.generate_public_filter() == False


def test_generate_private_filter(fg_class):
    fg_class._handle_cache = MagicMock(return_value=dummy_cache())
    fg_class.generate_public_filter()
    fg_class._handle_private_access = MagicMock(return_value=["dummy access"])
    fg_class._handle_cache = MagicMock(return_value=dummy_cache_private())
    assert (
        fg_class.generate_private_filter(["dummy access"])
        == dummy_filter_cache_private()
    )
