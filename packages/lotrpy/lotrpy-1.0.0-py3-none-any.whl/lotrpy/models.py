from typing import NamedTuple, List

class Movie(NamedTuple):
    """
    Class representing a movie object.
    """
    movie_id: str
    academy_award_nominations: int
    academy_award_wins: int
    box_office_revenue_in_millions: int
    budget_in_millions: int
    name: str
    rotten_tomatoes_score: int
    runtime_in_minutes: int

class Quote(NamedTuple):
    """
    Class representing a quote from an lotr movie.
    """
    quote_id: str
    movie_id: str
    dialog: str
    character: str

class BaseResponse(NamedTuple):
    limit: int
    # This is set to string though a number to accommodate for its conditional presence
    offset: str
    page: int
    pages: int
    total: int

class MovieListResponse(BaseResponse):
    movies: List[Movie]

class QuoteListResponse(BaseResponse):
    quotes: List[Quote]