import os
import json
from typing import List
import anthropic

from pathlib import Path
from dotenv import load_dotenv
from anthropic import beta_tool

load_dotenv(Path.home() / ".secrets")

base_url = os.environ.get("ANTHROPIC_BASE_URL")
auth_token = os.environ.get("ANTHROPIC_AUTH_TOKEN")

client = anthropic.Anthropic(auth_token=auth_token, base_url=base_url)


@beta_tool
def create_calender_event(
    title: str,
    start: str,
    end: str,
    attendees: List[str] | None = None,
    recurrence: dict | None = None,
):
    """Create a calendar event with attendees and optional recurrence.

    Args:
        title: Event title.
        start: Start time in ISO 8601 format.
        end: End time in ISO 8601 format.
        attendees: Email addresses to invite.
        recurrence: Dict with 'frequency' (daily, weekly, monthly) and 'count'.
    """
    if attendees and len(attendees) > 10:
        raise ValueError("Too many attendees (max 10)")
    return json.dumps({"event_id": "evt_123", "status": "created", "title": title})


@beta_tool
def list_calender_events(date: str) -> str:
    """List all calendar events on a given date.

    Args:
        date: Date in YYYY-MM-DD format.
    """
    return json.dumps(
        {"events": [{"title": "Existing meeting", "start": "14:00", "end": "15:00"}]}
    )


final_message = client.beta.messages.tool_runner(
    model="deepseek-v4-pro",
    max_tokens=10240,
    tools=[create_calender_event, list_calender_events],
    messages=[
        {
            "role": "user",
            "content": "Check what I have next Monday, then schedule a planning session that avoids any conflicts.",
        }
    ],
).until_done()

for block in final_message.content:
    if block.type == "text":
        print(block.text)
