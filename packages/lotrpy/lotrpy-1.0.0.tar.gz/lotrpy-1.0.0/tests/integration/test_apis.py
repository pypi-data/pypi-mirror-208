import pytest
from lotrpy.lotr import LOTR
from lotrpy.models import (
  Movie,
  MovieListResponse,
  Quote,
  QuoteListResponse
) 
from requests.exceptions import HTTPError

def test_get_movies(lotr_object):
    resp = lotr_object.get_movies()
    assert len(resp.movies) > 0

def test_get_movies_with_paging_and_limit(lotr_object):
    # we should received on page with 2 results with several pending
    # pages
    resp = lotr_object.get_movies(limit = 2)
    assert len(resp.movies) == 2
    assert resp.page < resp.pages

    # testing paging by fetching the next page
    next_page = lotr_object.get_movies(limit = 2, page = 2)
    assert len(next_page.movies) == 2
    assert next_page.page == resp.page + 1


def test_get_movie(lotr_object):
    resp = lotr_object.get_movie("5cd95395de30eff6ebccde5d")
    # import pdb;pdb.set_trace()
    assert isinstance(resp, Movie)
    assert resp.name

    # negative test
    with pytest.raises(HTTPError):
        resp = lotr_object.get_movie("bad_id")

def test_get_quote(lotr_object):
    resp = lotr_object.get_quote("5cd96e05de30eff6ebccebcf")
    # import pdb;pdb.set_trace()
    assert isinstance(resp, Quote)
    assert resp.dialog

    # negative test
    with pytest.raises(HTTPError):
        resp = lotr_object.get_quote("bad_id")


def test_get_quotes_from_movie(lotr_object):
    resp = lotr_object.get_quotes_from_movie("5cd95395de30eff6ebccde5b")
    assert len(resp.quotes) > 0
    assert isinstance(resp, QuoteListResponse)

def test_get_quotes(lotr_object):
    resp = lotr_object.get_quotes()
    assert len(resp.quotes) > 1
    assert isinstance(resp, QuoteListResponse)


def test_get_quotes_with_paging_and_limit(lotr_object):
    # we should have received one page with 2 results with several pending
    # pages
    resp = lotr_object.get_quotes(limit = 2)
    assert len(resp.quotes) == 2
    assert resp.page < resp.pages

    # testing paging by fetching the next page
    next_page = lotr_object.get_quotes(limit = 2, page = 2)
    assert len(next_page.quotes) == 2
    assert next_page.page == resp.page + 1


