# lotrpy SDK Design
The SDK follows a simple object oriented design. Code is split into multiple python modules for modularity and extension. These modules have the necessary classes & functions.

## Modules

1. lotr.py - has the main LOTR class
2. serializers.py - has deserializers for converting the json responses to python objects
3. models.py - has all the response classes

## Classes
LOTR: This is the main class that has all the methods corresponding to the movies, quote APIs. This class needs to be instantiated with the access token and server url for endpoints.

The url fragments for the endpoints themselves are built into the code as these are not expected to change often while the token and server base url need to be configurable.

Then there are various response objects corresponding to movies and quotes. Using clearly defined response
objects as opposed to the raw JSON returned by the API server makes it easy for python developers to reason
about while also making it possible to enforce compile time checks via mypy to ensure more correctness.


# Testing
The SDK comes with auomated unit and integration tests. Integration tests hit the API server. Deserializers have unit tests. Ideally we want unit tests covering the code paths that integration tests have covered as well but with mocked requests so we can execute faster and more frequently while integration tests will run less frequently to ensure the external API isn't broken from our perspective. But given the time constraints of this test, this seemed like a reasonable compromise. 
