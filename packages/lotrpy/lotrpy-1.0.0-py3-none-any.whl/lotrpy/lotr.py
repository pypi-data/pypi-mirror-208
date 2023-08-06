
import requests

from typing import NamedTuple, List, Union
from urllib.parse import urljoin
from lotrpy.serializers import (
    deserialize_movies, 
    deserialize_movie, 
    deserialize_quote,
    deserialize_quotes
)
from lotrpy.models import (
    Movie,
    MovieListResponse,
    Quote,
    QuoteListResponse
)

class LOTRException(Exception):
    pass

class LOTR():
    """
    This is the main class of this SDK that provides various methods to
    access movies, quotes from the API server.
    """
    def __init__(self, token, server_url):
        if not token or not server_url:
            raise LOTRException("token and server_url required")
        self.token = token
        self.server_url = server_url


    def get_movies(self, **kwargs: dict) -> MovieListResponse:
        """
        Fetches all the movies from the API server.

        Arguments:
            kwargs:
                limit: restrict the number of movies returned to this
                page: the page number to fetch
        
        Returns:
            ```MovieListResponse``` object
        """
        response = make_request(self.token, self.server_url, "movie", **kwargs)
        return deserialize_movies(response)

    def get_movie(self, movie_id: str) -> Union[Movie, None]:
        """
        Fetch a specific movie.

        Arguments:
            movie_id: ID of the movie to fetch.
        
        Returns:
            ```Movie``` object if present, None otherwise
        """
        response = make_request(self.token, self.server_url, f"movie/{movie_id}")
        return deserialize_movie(response)


    def get_quotes(self, **kwargs: dict) -> QuoteListResponse:
        """
        Fetches all the quotes from all movies.

        Arguments:
            kwargs:
                limit: restrict the number of quotes returned to this
                page: the page number to fetch
        
        Returns:
            ```QuoteListResponse``` object
        """
        response = make_request(self.token, self.server_url, f"quote", **kwargs)
        return deserialize_quotes(response)

    def get_quotes_from_movie(self, movie_id: str, **kwargs: dict) -> QuoteListResponse:
        """
        Fetches all the quotes from a specific movie.

        Arguments:
            kwargs:
                limit: restrict the number of movies returned to this
                page: the page number to fetch
        
        Returns:
            ```QuoteListResponse``` object
        """
        response = make_request(self.token, self.server_url, f"movie/{movie_id}/quote")
        return deserialize_quotes(response)

    def get_quote(self, quote_id: str) -> Union[Quote, None]:
        """
        Fetch a specific quote based on quote_id.

        Arguments:
            quote_id: ID of the quote
        
        Returns:
            ```Quote``` object for a valid quote_id or None if invalid.
        """
        response = make_request(self.token, self.server_url, f"quote/{quote_id}")
        return deserialize_quote(response)

def make_request(token, base_url, fragment, **kwargs):
    """
    Helper function that builds out the request, makes the call & handles response

    Arguments:
        token: The bearer token that the API server requires for most calls
        base_url: url of the server
        fragment: the url fragment for specific endpoint
        kwargs:
            page: page number to fetch the responses from 
            limit: the number of responses to limit to

    Returns:
        A JSON object
    """
    headers = {'Authorization': f'Bearer {token}'}
    url = urljoin(base_url, fragment)

    params = {}
    if "page" in kwargs:
        params["page"] = kwargs["page"]
    
    if "limit" in kwargs:
        params["limit"] = kwargs["limit"]

    if "offset" in kwargs:
        params["offset"] = kwargs["offset"]

    if params:
        response = requests.get(url, headers=headers, params=params)
    else:
        response = requests.get(url, headers=headers)
    # surface up the error to the consumer of our SDK. The deployed server api itself 
    # isn't detailed in this regard to supply more specific errors.
    response.raise_for_status()
    return response.json()