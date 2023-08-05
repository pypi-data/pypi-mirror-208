import typing


class SingleObjectsMixin:
    """Mixin class for an API endpoint that retrieves a single object.

    This mixin provides a `get` method for fetching a single object by its ID.
    If an object with the specified ID exists, the method returns the object;
    otherwise, it returns `None`.

    Usage:
        class MyObject(SingleObjectsMixin, Endpoint):
            ...

    In this example, `MyEndpoint` inherits both from `SingleObjectRetrievalMixin`
    and `BaseEndpoint`, and so it has a `get` method that fetches a single object.

    Methods:
        get(self, id: str) -> Optional[dict]:
            Fetch a single object by its ID.

            Args:
                id (str): The unique ID of the object to fetch.

            Returns:
                dict or None: The object, represented as a dictionary, if it exists;
                              otherwise, `None`.
    """

    def get(self, obj_id, *args, **kwargs) -> "typing.Optional[dict]":
        endpoint = self.endpoint + obj_id
        obj = self._make_request(endpoint, **kwargs)

        if obj is not None and "docs" in obj and len(obj["docs"]) == 1:
            return obj["docs"][0]
