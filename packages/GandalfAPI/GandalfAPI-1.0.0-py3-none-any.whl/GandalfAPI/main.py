import requests
from .utils import construct_params


class BaseAPI:
    BASE_URL = "https://the-one-api.dev/v2/"
    AUTH_HEADER = "Authorization"

    def __init__(self, api_key):
        self.api_key = api_key

    def _send_request(self, method, endpoint, params=None, data=None):
        headers = {self.AUTH_HEADER: f"Bearer {self.api_key}"}
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.request(
            method, url, headers=headers, params=params, json=data
        )

        if response.status_code == 401:
            raise InvalidApiKeyError("Invalid API key")
        if not response.ok:
            raise RequestFailedError(
                f"Request failed with status {response.status_code} and message {response.text}"
            )

        return response.json()


class MovieAPI(BaseAPI):
    def all(self, **params):
        """Get a list of all movies.

        Args:
            limit (int, optional): The number of results to return.
            offset (int, optional): The number of results to skip.

        Returns:
            dict: The JSON response from the API.
        """
        endpoint = "/movie"

        return self._send_request("GET", endpoint, params=params)

    def get(self, id):
        """Get a specific movie by ID.

        Args:
            id (str): The ID of the movie.

        Returns:
            dict: The JSON response from the API.
        """
        endpoint = f"movie/{id}"
        return self._send_request("GET", endpoint)

    def quotes(self, movie_id, **params):
        """Get the quotes for a specific movie.

        Args:
            **params: Additional query parameters to pass in the API request.
                Details:
                - Params for Pagination, Sorting, Filterin.
                - Help: https://the-one-api.dev/documentation

        Returns:
            dict: The JSON response from the API.
        """
        endpoint = f"movie/{movie_id}/quote"

        return self._send_request("GET", endpoint, params=params)


class QuoteAPI(BaseAPI):
    def all(self, **params):
        """Get a list of all quotes.

        Args:
            **params: Additional query parameters to pass in the API request.
                Details:
                - Params for Pagination, Sorting, Filterin.
                - Help: https://the-one-api.dev/documentation

        Returns:
            dict: The JSON response from the API.
        """
        endpoint = "/quote"

        return self._send_request("GET", endpoint, params=params)

    def get(self, id):
        """
        Get a specific quote by its ID.

        Args:
            id (str): The ID of the quote to retrieve.

        Returns:
            dict: A dictionary containing information about the quote, including its ID, dialogue, and character.

        Raises:
            ValueError: If the request fails for any reason, such as an invalid API key or non-existent quote ID.
        """
        endpoint = f"quote/{id}"
        return self._send_request("GET", endpoint)
