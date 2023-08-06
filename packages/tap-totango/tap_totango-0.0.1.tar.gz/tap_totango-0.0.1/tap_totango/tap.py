"""totango tap class."""

from __future__ import annotations

from typing import List

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_totango import streams


class Taptotango(Tap):
    """totango tap class."""

    name = "tap-totango"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_url",
            th.StringType,
            default="https://api.totango.com",
            description="The url for the API service",
        ),
        th.Property(
            "auth_token",
            th.StringType,
            required=True,
            secret=True,  # Flag config as protected.
            description="The token to authenticate against the API service",
        ),
        th.Property(
            "terms",
            th.ArrayType(
                th.ObjectType(
                    th.Property("type", th.StringType, required=True),
                    additional_properties=True,
                )
            ),
            required=True,
            default=[],
            description="An array containing filter conditions to use for the search.",
        ),
        th.Property(
            "count",
            th.IntegerType,
            required=True,
            default=5,
            description="The maximum number of accounts to return in the result set. The max. value for count is 1000.",
        ),
        th.Property(
            "offset",
            th.IntegerType,
            required=True,
            default=0,
            description="Page number (0 is the 1st-page).",
        ),
        th.Property(
            "account_id",
            th.StringType,
            description="Filter the results for a specific account.",
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.totangoStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [streams.EventsStream(self)]


if __name__ == "__main__":
    Taptotango.cli()
