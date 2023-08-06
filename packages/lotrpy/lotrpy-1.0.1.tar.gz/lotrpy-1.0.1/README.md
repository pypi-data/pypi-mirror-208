# dinesh_ketumakha-SDK

This is the python sdk for accessing https://the-one-api.dev/ server's endpoints related to Lord Of the Rings movies & quotes.

# Installation
To install using ``pip`` do the following in a virtual environment

    $ mkdir my_lotr_test_dir
    $ cd my_lotr_test_dir
    $ python3 -m venv venv
    $ pip install lotrpy


# Usage

The following is how you can use this SDK

    from lotrpy.lotr import LOTR
    
    token = "bearer_token_value"
    base_url = "https"//server.com/api/v1"

    lotr = LOTR(token, base_url)
    
    # get all movies
    lotr.get_movies()

    # get all movies on page 2 if there was more than 1 page 
    # in the response above
    lotr.get_movies(page=2)

    # get all movies, limit each response to 5  items
    lotr.get_movies(limit = 5)

    # get info on a single movie
    movie_id = "123lkdlfs"
    lotr.get_movie(movie_id)

    # get all quotes. paging and limit apply just like above
    lotr.get_quotes()

    # get all quotes from one specific movie
    lotr.get_quotes_from_movie(movie_id)

    # get one specific quote. Need to get the quote_id from 
    # response of get_quotes()
    lotr.get_quote(quote_id) 


# Testing

To run the tests, install pytest in the venv created above

    $ pip install pytest

Clone this repo and cd into the root of the directory

    $ git clone https://github.com/gypsyx/dinesh_ketumakha-SDK.git

    $ cd dinesh_ketumakha-SDK
    $ pytest # runs all tests

To run just unit tests

    $ pytest -k unit

 