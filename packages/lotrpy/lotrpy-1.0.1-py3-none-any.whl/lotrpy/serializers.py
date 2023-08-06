# Serializers & Deserializers module

from typing import Union
from lotrpy.models import (
    Movie,
    MovieListResponse,
    Quote,
    QuoteListResponse
)

def deserialize_movies(movies: dict) -> MovieListResponse:
    resp = MovieListResponse(
        limit = movies['limit'],
        offset = str(movies['offset']) if "offset" in movies else "",
        page = movies['page'],
        pages = movies['pages'],
        total = movies['total'],
    )
    resp.movies = []
    for movie in movies['docs']:
        item = Movie(
            movie_id = movie["_id"],
            academy_award_nominations= movie["academyAwardNominations"],
            academy_award_wins= movie["academyAwardWins"],
            box_office_revenue_in_millions= movie["boxOfficeRevenueInMillions"],
            budget_in_millions= movie["budgetInMillions"],
            rotten_tomatoes_score= movie["rottenTomatoesScore"],
            runtime_in_minutes= movie["runtimeInMinutes"],
            name = movie["name"]
        )
        resp.movies.append(item)
    
    return resp


def deserialize_movie(movie: dict) -> Union[Movie, None]:
    if not movie["docs"]:
        return None
    
    # this call should never return more than one item in response
    movie = movie["docs"][0]
    
    return Movie(
        movie_id = movie["_id"],
        academy_award_nominations= movie["academyAwardNominations"],
        academy_award_wins= movie["academyAwardWins"],
        box_office_revenue_in_millions= movie["boxOfficeRevenueInMillions"],
        budget_in_millions= movie["budgetInMillions"],
        rotten_tomatoes_score= movie["rottenTomatoesScore"],
        runtime_in_minutes= movie["runtimeInMinutes"],
        name = movie["name"]
    )

def deserialize_quote(quote: dict) -> Union[Quote, None]:
    if not quote["docs"]:
        return None
    
    # this call should never return more than one item in response
    quote = quote["docs"][0]

    return Quote(
        quote_id = quote["_id"],
        movie_id = quote["movie"],
        dialog = quote["dialog"],
        character = quote["character"]
    )

def deserialize_quotes(quotes: dict) -> QuoteListResponse:
    resp = QuoteListResponse(
        limit = quotes['limit'],
        offset = str(quotes['offset']) if "offset" in quotes else "",
        page = quotes['page'],
        pages = quotes['pages'],
        total = quotes['total'],
    )
    resp.quotes = []
    for quote in quotes['docs']:
        item = Quote(
            quote_id = quote["_id"],
            movie_id = quote["movie"],
            dialog = quote["dialog"],
            character = quote["character"]
        )
        resp.quotes.append(item)
    
    return resp


