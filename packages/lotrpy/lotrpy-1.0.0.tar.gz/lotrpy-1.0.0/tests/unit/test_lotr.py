import pytest
from lotrpy.lotr import LOTR, LOTRException
from lotrpy.serializers import (
    deserialize_movie,
    deserialize_movies,
    deserialize_quote,
    deserialize_quotes
)
from lotrpy.models import (
    Movie,
    MovieListResponse,
    Quote,
    QuoteListResponse,
)

def test_LOTR():
    with pytest.raises(LOTRException):
        LOTR("" , "")

def test_deserialize_movie(movie):
    resp = deserialize_movie(movie)
    movie = movie["docs"][0]
    assert isinstance(resp, Movie)
    assert resp.name == "The Hobbit Series"
    assert resp.movie_id == "5cd95395de30eff6ebccde57"
    assert resp.academy_award_nominations == 7
    assert resp.box_office_revenue_in_millions == 2932
    assert resp.budget_in_millions == 675
    assert resp.rotten_tomatoes_score == 66.33333333
    assert resp.runtime_in_minutes == 462

def test_deserialize_movie_negative(movie):
    movie["docs"].clear()
    assert not deserialize_movie(movie)


def test_deserialize_movies(movies):
    resp = deserialize_movies(movies)
    assert isinstance(resp, MovieListResponse)
    assert resp.limit == 2
    assert resp.page == 1
    assert resp.total == 8
    assert resp.pages == 4
    assert resp.offset == 0
    assert len(resp.movies) == 2
    assert resp.movies[0].name == "The Lord of the Rings Series"
    assert resp.movies[1].name == "The Hobbit Series"

def test_deserialize_quote(quote):
    resp = deserialize_quote(quote)
    assert isinstance(resp, Quote)
    assert resp.quote_id == "5cd96e05de30eff6ebcce7e9"
    assert resp.dialog == "Deagol!"
    assert resp.movie_id == "5cd95395de30eff6ebccde5d"

def test_deserialize_quote_negative(quote):
    quote["docs"].clear()
    assert not deserialize_movie(quote)

def test_deserialize_quotes(quotes):
    resp = deserialize_quotes(quotes)
    assert isinstance(resp, QuoteListResponse)
    assert len(resp.quotes) == 2
    assert resp.quotes[0].dialog == "Deagol!"
    assert resp.quotes[1].dialog == "Deagol Deagol!"
    assert resp.quotes[0].quote_id == "5cd96e05de30eff6ebcce7e9"
    assert resp.quotes[1].quote_id == "5cd96e05de30eff6ebcce7ea"

