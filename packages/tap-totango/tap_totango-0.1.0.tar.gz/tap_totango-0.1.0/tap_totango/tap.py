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
            "events_terms",
            th.ArrayType(
                th.ObjectType(
                    th.Property("type", th.StringType, required=True),
                    additional_properties=True,
                )
            ),
            required=True,
            default=[],
            description="An array containing filter conditions to use for the events stream search.",
        ),
        th.Property(
            "events_count",
            th.IntegerType,
            required=True,
            default=5,
            description="The maximum number of accounts to return in the events result set. The max. value for count is 1000.",
        ),
        th.Property(
            "events_offset",
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
        th.Property(
            "accounts_terms",
            th.ArrayType(
                th.ObjectType(
                    th.Property("type", th.StringType, required=True),
                    additional_properties=True,
                )
            ),
            required=True,
            default=[],
            description="An array containing filter conditions to use for the accounts stream search.",
        ),
        th.Property(
            "accounts_fields",
            th.ArrayType(
                th.ObjectType(
                    th.Property("type", th.StringType, required=True),
                    additional_properties=True,
                )
            ),
            required=True,
            default=[],
            description="List of fields to return as results. Note that the account name and account-id are always returned as well.",
        ),
        th.Property(
            "accounts_count",
            th.IntegerType,
            default=1000,
            description="The maximum number of accounts to return in the events result set. The max. value for count is 1000.",
        ),
        th.Property(
            "accounts_offset",
            th.IntegerType,
            default=0,
            description='Record number (0 states "start at record 0"). The record size can be defined using the count parameter (and limited to 1000). Tip: To page through results, ask for 1000 records (count: 1000). If you receive 1000 records, assume there’s more, in which case you want to pull the next 1000 records (offset: 1000…then 2000…etc.). Repeat paging until the number of records returned is less than 1000.',
        ),
        th.Property(
            "accounts_sort_by",
            th.StringType,
            default="display_name",
            description="Field name to sort the accounts stream results set by.",
        ),
        th.Property(
            "accounts_sort_order",
            th.StringType(allowed_values=["ASC", "DESC"]),
            default="ASC",
            description="Order to sort the accounts stream results set by.",
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.totangoStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [streams.EventsStream(self), streams.AccountsStream(self)]


if __name__ == "__main__":
    Taptotango.cli()
