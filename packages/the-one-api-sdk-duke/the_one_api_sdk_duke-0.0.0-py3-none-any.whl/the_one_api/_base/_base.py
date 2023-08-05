import abc
import json
import typing

import requests

from the_one_api import errors


class Endpoint(metaclass=abc.ABCMeta):
    """
    Abstract Base Class representing a general API endpoint.

    This class provides the basic structure and methods for managing API endpoints,
    including handling URLs and authentication requirements.

    Each endpoint object is associated with a specific route and has a flag to indicate
    whether it requires authentication.

    Attributes
    ----------
    requires_auth : bool
        A flag indicating whether this endpoint requires authentication.
        By default, it's set to False.

    route : str
        The base route for the endpoint.

    Methods
    -------
    _make_request(endpoint):
        Creates the conditions needed for a successful GET call, including
        constructing a complete URL for the required endpoint and ensuring
        headers are set appropriately.
    """

    requires_auth = False
    route = "https://the-one-api.dev/v2/"

    def _make_request(self, endpoint: str, **kwargs) -> dict:
        """
        Makes a GET request to the given endpoint and returns the response.

        This method combines base route and the provided URL path to form the full URL,
        sets the Authorization header if required, and makes the HTTP request.

        Parameters
        ----------
        endpoint : str
            The last part of the URL for the API endpoint. This will be appended
            to the base route to form the full URL. For example, if the base route
            is 'https://api.example.com/v1/' and the endpoint is 'users', the full
            URL will be 'https://api.example.com/v1/users'.

        **kwargs : dict, optional
            Arbitrary keyword arguments. These will be forwarded to the underlying
            HTTP request function. This can be used to pass parameters like headers,
            data, params, etc. For example, if you pass `params={'key': 'value'}`,
            it will add '?key=value' to the URL.

        Returns
        -------
        response : dict
            The dumped JSON content from the HTTP response.

        Raises
        ------
        APIError
            If the response received is not ok (e.g. a 404 error HTML page for
            a non-existent endpoint)
        """

        url: str = self.route + endpoint
        headers: typing.Dict[str] = {}
        if self.requires_auth:
            from the_one_api import api_key

            headers["Authorization"] = f"Bearer {api_key}"

        response = requests.get(url, headers=headers)
        if response.ok:
            return response.json()

        try:
            error_message = response.json().get("message")
        except json.JSONDecodeError:
            error_message = response.text

        raise errors.APIError(error_message)
