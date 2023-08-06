"""Stream type classes for tap-totango."""

from __future__ import annotations

from pathlib import Path
import typing as t

import json
from singer_sdk import typing as th
from singer_sdk._singerlib import Schema
from singer_sdk.tap_base import Tap  # JSON Schema typing helpers


from tap_totango.client import totangoStream

# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")
# TODO: - Override `UsersStream` and `GroupsStream` with your own stream definition.
#       - Copy-paste as many times as needed to create multiple stream types.


class AccountsStream(totangoStream):
    """Define custom stream."""

    name = "accounts"
    rest_method = "POST"

    path = "/api/v1/search/accounts"

    records_jsonpath = "$.response.accounts.hits[*]"
    primary_keys = ["name"]
    replication_key = None
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    schema_filepath = SCHEMAS_DIR / "accounts.json"  # noqa: ERA001

    def prepare_request_payload(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: t.Any | None,  # noqa: ARG002
    ) -> dict | None:
        """Prepare the data payload for the REST API request.

        By default, no payload will be sent (return None).

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary with the JSON body for a POST requests.
        """
        # TODO: Delete this method if no payload is required. (Most REST APIs.)
        params = self.config
        query = {
            "terms": params["accounts_terms"],
            "fields": params["accounts_fields"],
            "offset": params["accounts_offset"],
            "count": params["accounts_count"],
            "sort_by": params["accounts_sort_by"],
            "sort_order": params["accounts_sort_order"],
        }
        data = {"query": json.dumps(query)}
        return data

    def get_child_context(self, record: dict, context: t.Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "account_id": record["name"],
        }


class UsersStream(totangoStream):
    """Define custom stream."""

    name = "users"
    rest_method = "POST"

    path = "/api/v1/search/users"

    records_jsonpath = "$.response.users.hits[*]"
    primary_keys = ["name"]
    replication_key = None
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    schema_filepath = SCHEMAS_DIR / "users.json"  # noqa: ERA001

    def prepare_request_payload(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: t.Any | None,  # noqa: ARG002
    ) -> dict | None:
        """Prepare the data payload for the REST API request.

        By default, no payload will be sent (return None).

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary with the JSON body for a POST requests.
        """
        # TODO: Delete this method if no payload is required. (Most REST APIs.)
        params = self.config
        query = {
            "terms": params["users_terms"],
            "fields": params["users_fields"],
            "offset": params["users_offset"],
            "count": params["users_count"],
            "sort_by": params["users_sort_by"],
            "sort_order": params["users_sort_order"],
        }
        data = {"query": json.dumps(query)}
        return data


class EventsStream(totangoStream):
    """Define custom stream."""

    name = "events"
    rest_method = "POST"

    path = "/api/v2/events/search"

    records_jsonpath = "$.response.events.hits[*]"
    primary_keys = ["id"]
    replication_key = None
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    schema_filepath = SCHEMAS_DIR / "events.json"  # noqa: ERA001

    parent_stream_type = AccountsStream
    ignore_parent_replication_key = True

    def prepare_request_payload(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: t.Any | None,  # noqa: ARG002
    ) -> dict | None:
        """Prepare the data payload for the REST API request.

        By default, no payload will be sent (return None).

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary with the JSON body for a POST requests.
        """
        # TODO: Delete this method if no payload is required. (Most REST APIs.)
        params = self.config
        query = {
            "terms": params["events_terms"],
            "fields": [],
            "offset": params["events_offset"],
            "count": params["events_count"],
        }
        data = {"query": json.dumps(query)}
        data["account_id"] = "{account_id}"
        return data
