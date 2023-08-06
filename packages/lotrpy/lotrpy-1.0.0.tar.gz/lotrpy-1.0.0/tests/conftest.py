import pytest
from lotrpy.lotr import LOTR

# This should be the testing token, so okay to have it here
TOKEN = "KkyexrFGQBW5wPJcNTKY"
SERVER_URL = "https://the-one-api.dev/v2/"

@pytest.fixture
def lotr_object():
    response = LOTR(token=TOKEN, server_url=SERVER_URL)
    return response

@pytest.fixture
def movie():
    return {
        'docs': [{'_id': '5cd95395de30eff6ebccde57',
           'academyAwardNominations': 7,
           'academyAwardWins': 1,
           'boxOfficeRevenueInMillions': 2932,
           'budgetInMillions': 675,
           'name': 'The Hobbit Series',
           'rottenTomatoesScore': 66.33333333,
           'runtimeInMinutes': 462}],
        'limit': 1000,
        'offset': 0,
        'page': 1,
        'pages': 1,
        'total': 1}


@pytest.fixture
def movies():
    return {
        'docs': [ { '_id': '5cd95395de30eff6ebccde56',
                    'academyAwardNominations': 30,
                    'academyAwardWins': 17,
                    'boxOfficeRevenueInMillions': 2917,
                    'budgetInMillions': 281,
                    'name': 'The Lord of the Rings Series',
                    'rottenTomatoesScore': 94,
                    'runtimeInMinutes': 558},
                    { '_id': '5cd95395de30eff6ebccde57',
                    'academyAwardNominations': 7,
                    'academyAwardWins': 1,
                    'boxOfficeRevenueInMillions': 2932,
                    'budgetInMillions': 675,
                    'name': 'The Hobbit Series',
                    'rottenTomatoesScore': 66.33333333,
                    'runtimeInMinutes': 462}],
        'limit': 2,
        'offset': 0,
        'page': 1,
        'pages': 4,
        'total': 8}

@pytest.fixture
def quotes():
    return {'docs': [{'_id': '5cd96e05de30eff6ebcce7e9',
                    'character': '5cd99d4bde30eff6ebccfe9e',
                    'dialog': 'Deagol!',
                    'id': '5cd96e05de30eff6ebcce7e9',
                    'movie': '5cd95395de30eff6ebccde5d'},
                    {'_id': '5cd96e05de30eff6ebcce7ea',
                    'character': '5cd99d4bde30eff6ebccfe9e',
                    'dialog': 'Deagol Deagol!',
                    'id': '5cd96e05de30eff6ebcce7ea',
                    'movie': '5cd95395de30eff6ebccde5de'}],
            'limit': 2,
            'offset': 0,
            'page': 1,
            'pages': 1192,
            'total': 2384}

@pytest.fixture
def quote():
    return {'docs': [{'_id': '5cd96e05de30eff6ebcce7e9',
                    'character': '5cd99d4bde30eff6ebccfe9e',
                    'dialog': 'Deagol!',
                    'id': '5cd96e05de30eff6ebcce7e9',
                    'movie': '5cd95395de30eff6ebccde5d'}],
            'limit': 1000,
            'offset': 0,
            'page': 1,
            'pages': 1,
            'total': 1}