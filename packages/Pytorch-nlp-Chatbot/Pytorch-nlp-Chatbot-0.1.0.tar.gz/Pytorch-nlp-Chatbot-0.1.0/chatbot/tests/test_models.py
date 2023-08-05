# Authors: Koro_Is_Coding
# License: Apache v2.0

# standard libraries


# external libraries
import pytest
from io import StringIO

# module to be tested
from chatbot import SearchEngineStruct
from chatbot import SearchException


def test_se_default_init():
    se = SearchEngineStruct()
    assert se.google_api_key == "AIzaSyAGHYwrgMmAHlFwM-GmS2anQ7xWu7qcIjA"
    assert se.google_engine_key == "7a8bd65adc0b760d8"
    assert se.top_result == list()
    assert se.relevant == list()
    assert se.irrelevant == list()
    assert se.query == ""


def test_se_api_init():
    google_api_key = "api"
    google_engine_key = "engine"
    se = SearchEngineStruct(google_api_key, google_engine_key)
    assert se.google_api_key == "api"
    assert se.google_engine_key == "engine"
    assert se.top_result == list()
    assert se.relevant == list()
    assert se.irrelevant == list()
    assert se.query == ""


def test_get_top_result_empty():
    se = SearchEngineStruct()
    assert len(SearchEngineStruct.get_top_result(se)) == 0


def test_set_and_get_query():
    se = SearchEngineStruct()
    seed_query = "test_query"
    se.set_query(seed_query)
    assert se.get_query() == seed_query


def test_search_current_query_google_success():
    se = SearchEngineStruct()
    seed_query = "per se"
    se.set_query(seed_query)
    se.call_google_custom_search_api()
    assert len(se.get_top_result()) >= 10


def test_search_current_query_google_fail():
    se = SearchEngineStruct()
    seed_query = "jjj sedskdsksdkdskdskdskdkssdkds"
    se.set_query(seed_query)
    with pytest.raises(SearchException):
        se.call_google_custom_search_api()


def test_choose_relevant_1(monkeypatch):
    number_inputs = StringIO("Y\n" * 10)
    se = SearchEngineStruct()
    seed_query = "per se"
    se.set_query(seed_query)
    se.call_google_custom_search_api()
    monkeypatch.setattr("sys.stdin", number_inputs)
    assert se.choose_relevant() == 1
    assert len(se.relevant) == 10
    assert len(se.irrelevant) == 0


def test_choose_relevant_0(monkeypatch):
    number_inputs = StringIO("N\n" * 10)
    se = SearchEngineStruct()
    seed_query = "per se"
    se.set_query(seed_query)
    se.call_google_custom_search_api()
    monkeypatch.setattr("sys.stdin", number_inputs)
    assert se.choose_relevant() == 0
    assert len(se.relevant) == 0
    assert len(se.irrelevant) == 10
