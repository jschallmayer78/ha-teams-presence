"""Constants for the Microsoft Teams Presence integration."""

from __future__ import annotations

from datetime import timedelta
from typing import Final

DOMAIN: Final = "teams_presence"

# "organizations" works for multi-tenant app registrations
# ("Accounts in any organizational directory"). For a single-tenant app,
# the tenant ID can be set via TENANT below.
TENANT: Final = "organizations"
OAUTH2_AUTHORIZE: Final = (
    f"https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/authorize"
)
OAUTH2_TOKEN: Final = f"https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/token"

SCOPES: Final = ["offline_access", "User.Read", "Presence.Read"]

GRAPH_BASE_URL: Final = "https://graph.microsoft.com/v1.0"

CONF_SCAN_INTERVAL: Final = "scan_interval"
DEFAULT_SCAN_INTERVAL: Final = 30  # seconds
MIN_SCAN_INTERVAL: Final = 10
MAX_SCAN_INTERVAL: Final = 3600
DEFAULT_UPDATE_INTERVAL: Final = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

# https://learn.microsoft.com/graph/api/resources/presence
AVAILABILITY_STATES: Final = [
    "available",
    "available_idle",
    "away",
    "be_right_back",
    "busy",
    "busy_idle",
    "do_not_disturb",
    "offline",
    "presence_unknown",
]

ACTIVITY_STATES: Final = [
    "available",
    "away",
    "be_right_back",
    "busy",
    "do_not_disturb",
    "in_a_call",
    "in_a_conference_call",
    "inactive",
    "in_a_meeting",
    "offline",
    "off_work",
    "out_of_office",
    "presence_unknown",
    "presenting",
    "urgent_interruptions_only",
]

# Activities that count as "in a call / meeting"
CALL_ACTIVITIES: Final = {
    "in_a_call",
    "in_a_conference_call",
    "in_a_meeting",
    "presenting",
}
