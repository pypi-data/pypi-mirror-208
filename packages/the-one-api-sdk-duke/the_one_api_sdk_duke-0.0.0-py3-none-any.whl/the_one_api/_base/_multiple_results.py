import typing


class Filter:
    """
    A class to collect sort/filter input from a user and transform it into
    query parameters suitable for a third-party API.

    This class supports a range of functionalities, allowing users to specify
    how data should be sorted and filtered.

    Functionalities:
     1. Sort: Order the results based on one field.
     2. Match: Filter the results based on matching a specific criteria.
     3. Negate Match: Filter the results based on not matching a specific criteria.
     4. Filter: Apply a list of matches to filter the results.
     5. Exclude: Apply a list of negated matches to filter the results.
     6. Regex: Apply a MongoDB-style regular expression to filter the results.
     7. Negate Regex: Apply a negated MongoDB-style regular expression to filter
        the results.
     8. Less Than: Return results only where the matches are less than the criteria.
     8. Greater Than: Return results only where the matches are greater than the
        criteria.
    10. Greater Than or Equal: Return results only where the matches are greater
        than or equal to the criteria.

    These functionalities give users a high degree of control over the data
    that is returned from the API.
    """

    def __init__(self, **kwargs):
        self.filters = {
            "sort": kwargs.get("sort"),
            "match": kwargs.get("match"),
            "negate_match": kwargs.get("negate_match"),
            "filter": kwargs.get("filter"),
            "exclude": kwargs.get("exclude"),
            "regex": kwargs.get("regex"),
            "negate_regex": kwargs.get("negate_regex"),
            "lt": kwargs.get("lt"),
            "gt": kwargs.get("gt"),
            "gte": kwargs.get("gte"),
        }

        self.parse_kwargs()

    @property
    def query_params(self):
        return "&".join([f"{value}" for value in self.filters.values() if value])

    def parse_sort(self):
        """Transforms the instance filter's sort value into a query parameter.

        The sort value should be a string.
        """
        sort = self.filters["sort"]
        if sort.startswith("-"):
            sort = f"sort={sort[1:]}:desc"
        else:
            sort = f"sort={sort}:asc"
        self.filters["sort"] = sort

    def _parse_singles(
        self, joiner, dictionary: typing.Dict[str, typing.Union[str, int]]
    ) -> str:
        """Create a query parameter from the key/value provided in the dictionary
        using the joiner (e.g. '=').

        Don't assume the value is a string.
        """
        attribute, criterion = list(dictionary.items())[0]
        return f"{attribute}{joiner}{criterion}"

    def _parse_multiples(
        self, joiner, dictionary: typing.Dict[str, typing.Union[str, int]]
    ) -> str:
        """Create a query parameter from the key/value provided in the dictionary
        using the joiner (e.g. '=').

        The value is assumed to be a list or tuple. Don't assume the contents are
        all strings.
        """
        attribute, criteria = list(dictionary.items())[0]
        joined_criteria = ",".join([str(criterion) for criterion in criteria])
        return f"{attribute}{joiner}{joined_criteria}"

    def parse_match(self):
        """Transforms the instance filter's match value into a query parameter.

        The match value should be a dictionary containing an attribute and
        a value (e.g. `{"attribute": "match_value"}
        """
        match = self.filters["match"]
        self.filters["match"] = self._parse_singles("=", match)

    def parse_negate_match(self):
        """Transforms the instance filter's negate match value into a query parameter.

        The match value should be a dictionary containing an attribute and
        a value to not be matched (e.g. `{"attribute": "dont_match_value"}
        """
        match = self.filters["negate_match"]
        self.filters["negate_match"] = self._parse_singles("!=", match)

    def parse_filter(self):
        """Transforms the instance filter's filter value into a query parameter.

        The match value should be a dictionary containing an attribute and
        a list of values to match (e.g. `{"attribute": ["match_value1", "match_value2"]}
        """

        results_filter = self.filters["filter"]
        self.filters["filter"] = self._parse_multiples("=", results_filter)

    def parse_exclude(self):
        """Transforms the instance filter's exclude value into a query parameter.

        The match value should be a dictionary containing an attribute and
        a list of values to not match.
        E.g. `{"attribute": ["dont_match_value1", "dont_match_value2"]}`
        """

        exclude = self.filters["exclude"]
        self.filters["exclude"] = self._parse_multiples("!=", exclude)

    def parse_regex(self):
        """Transforms the instance filter's regex value into a query parameter.

        The match value should be a dictionary containing an attribute and
        a regex pattern to be matched (e.g. `{"attribute": "match_pattern"}
        """
        match = self.filters["regex"]
        self.filters["regex"] = self._parse_singles("=", match)

    def parse_negate_regex(self):
        """Transforms the instance filter's regex value into a query parameter.

        The match value should be a dictionary containing an attribute and
        a pattern to not be matched (e.g. `{"attribute": "dont_match_pattern"}
        """
        match = self.filters["negate_regex"]
        self.filters["negate_regex"] = self._parse_singles("!=", match)

    def parse_lt(self):
        """Transforms the instance filter's 'less than' value into a query parameter.

        The match value should be a dictionary containing an attribute
        and a value to compare.
        """
        less_than = self.filters["lt"]
        self.filters["lt"] = self._parse_singles("<", less_than)

    def parse_gt(self):
        """Transforms the instance filter's 'greater than' value into a query parameter.

        The match value should be a dictionary containing an attribute
        and a value to compare.
        """
        greater_than = self.filters["gt"]
        self.filters["gt"] = self._parse_singles(">", greater_than)

    def parse_gte(self):
        """Transforms the instance filter's 'greater than or equal' value into
        a query parameter.

        The match value should be a dictionary containing an attribute
        and a value to compare.
        """
        greater_than = self.filters["gte"]
        self.filters["gte"] = self._parse_singles(">=", greater_than)

    def parse_kwargs(self):
        """Parse each of the supported sort/filter functionalities."""
        for filter_key, value in self.filters.items():
            if value:
                eval(f"self.parse_{filter_key}")()


class MultipleObjectsMixin:
    def list_all(self, *args, **kwargs):
        return self.filter()

    def filter(self, *args, **kwargs):
        endpoint = self.endpoint
        if "endpoint" in kwargs:
            endpoint = kwargs.pop("endpoint")
        params = Filter(**kwargs).query_params if kwargs else ""
        objs = self._make_request("?".join([endpoint, params]), **kwargs)

        if objs is not None and "docs" in objs:
            return objs["docs"]
