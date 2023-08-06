"""Stream type classes for tap-totango."""

from __future__ import annotations

from pathlib import Path
import typing as t

from singer_sdk import typing as th
from singer_sdk._singerlib import Schema
from singer_sdk.tap_base import Tap  # JSON Schema typing helpers

from tap_totango.client import totangoStream

# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")
# TODO: - Override `UsersStream` and `GroupsStream` with your own stream definition.
#       - Copy-paste as many times as needed to create multiple stream types.


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
