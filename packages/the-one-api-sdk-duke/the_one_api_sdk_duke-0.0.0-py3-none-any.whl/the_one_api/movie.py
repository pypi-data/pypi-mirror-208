import typing

from the_one_api._base._base import Endpoint
from the_one_api._base._multiple_results import MultipleObjectsMixin
from the_one_api._base._single_results import SingleObjectsMixin


class Movie(MultipleObjectsMixin, SingleObjectsMixin, Endpoint):
    """The Movie endpoint."""

    requires_auth = True
    endpoint = "movie/"


def get(movie_id: str) -> dict:
    """Fetch a movie by its id."""

    return Movie().get(movie_id)


def list_all() -> typing.List[dict]:
    """List all movies in the database."""

    return Movie().list_all()


def filter(
    sort: str = None,
    match: typing.Dict[str, typing.Any] = None,
    negate_match: typing.Dict[str, typing.Any] = None,
    filter: typing.Dict[str, typing.List[typing.Any]] = None,
    exclude: typing.Dict[str, typing.List[typing.Any]] = None,
    regex: typing.Dict[str, str] = None,
    negate_regex: typing.Dict[str, str] = None,
    lt: typing.Dict[str, typing.Any] = None,
    gt: typing.Dict[str, typing.Any] = None,
    gte: typing.Dict[str, typing.Any] = None,
) -> typing.List[dict]:
    """List and optionally sort movies filtered by any of the criteria mentioned below.

    Kwargs:
        sort (str): The attribute to sort by. Prefix with "-" for descending order.
        match (dict): Dictionary with attribute as key and string to match as value.
        negate_match (dict): Dictionary with attribute as key and string not to match
                             as value.
        filter (dict): Dictionary with attribute as key and list of strings to match
                       as value.
        exclude (dict): Dictionary with attribute as key and list of strings not to
                        match as value.
        regex (dict): Dictionary with attribute as key and regex pattern as value.
        negate_regex (dict): Dictionary with attribute as key and regex pattern not
                             to match as value.
        lt (dict): Dictionary with attribute as key and value that attribute should
                   be less than.
        gt (dict): Dictionary with attribute as key and value that attribute should
                   be greater than.
        gte (dict): Dictionary with attribute as key and value that attribute should
                    be greater than or equal to.

    Returns:
        A list of the matching results.
    """

    return Movie().filter(
        sort=sort,
        match=match,
        negate_match=negate_match,
        filter=filter,
        exclude=exclude,
        regex=regex,
        negate_regex=negate_regex,
        lt=lt,
        gt=gt,
        gte=gte,
    )
