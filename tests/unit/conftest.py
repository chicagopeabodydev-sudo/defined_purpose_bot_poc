import pytest
import src.tools.take_order as _take_order_mod
import src.tools.answer_menu_question as _answer_menu_mod
import src.tools.get_error_response as _error_mod
import src.tools.get_non_error_response as _non_error_mod
import src.tools.summarize_order as _summarize_order_mod


@pytest.fixture
def reset_take_order_cache():
    _take_order_mod._menu = None
    yield
    _take_order_mod._menu = None


@pytest.fixture
def reset_answer_menu_cache():
    _answer_menu_mod._menu = None
    yield
    _answer_menu_mod._menu = None


@pytest.fixture
def reset_error_cache():
    _error_mod._error_messages = None
    yield
    _error_mod._error_messages = None


@pytest.fixture
def reset_non_error_cache():
    _non_error_mod._non_error_messages = None
    yield
    _non_error_mod._non_error_messages = None


@pytest.fixture
def reset_summarize_order_cache():
    _summarize_order_mod._menu = None
    yield
    _summarize_order_mod._menu = None
