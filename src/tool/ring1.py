import os
import json
import httpx
import anthropic

from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path.home() / ".secrets")

# Check calendar credentials before making a billed model request.
calendar_access_token = os.environ.get("GOOGLE_CALENDAR_ACCESS_TOKEN", "").strip()
if not calendar_access_token:
    raise SystemExit(
        "Missing GOOGLE_CALENDAR_ACCESS_TOKEN. Add a Google OAuth access token "
        "with calendar.events permission to ~/.secrets before running this script."
    )

client = anthropic.Anthropic()

# Define one tool. The input_schema is a JSON Schema object describing
# the arguments Claude should pass when it calls this tool. This schema
# includes nested objects (recurrence), arrays (attendees), and optional
# fields, which is closer to real-world tools than a flat string argument.
tools = [
    {
        "name": "create_calendar_event",
        "description": "Create a calendar event with attendees and optional recurrence.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "start": {"type": "string", "format": "date-time"},
                "end": {"type": "string", "format": "date-time"},
                "attendees": {
                    "type": "array",
                    "items": {"type": "string", "format": "email"},
                },
                "recurrence": {
                    "type": "object",
                    "properties": {
                        "frequency": {"enum": ["daily", "weekly", "monthly"]},
                        "count": {"type": "integer", "minimum": 1},
                    },
                },
            },
            "required": ["title", "start", "end"],
        },
    }
]


def create_calendar_event(tool_input: dict) -> dict:
    event = {
        "summary": tool_input["title"],
        "start": {
            "dateTime": tool_input["start"],
            "timeZone": "America/Los_Angeles",
        },
        "end": {
            "dateTime": tool_input["end"],
            "timeZone": "America/Los_Angeles",
        },
        "attendees": [{"email": email} for email in tool_input.get("attendees", [])],
    }

    recurrence = tool_input.get("recurrence")
    if recurrence:
        frequencies = {
            "daily": "DAILY",
            "weekly": "WEEKLY",
            "monthly": "MONTHLY",
        }
        rule = f"RRULE:FREQ={frequencies[recurrence['frequency']]}"
        if "count" in recurrence:
            count = int(recurrence["count"])
            if count < 1:
                raise ValueError("Recurrence count must be positive")
            rule += f";COUNT={count}"
        event["recurrence"] = [rule]

    response = httpx.post(
        "https://www.googleapis.com/calendar/v3/calendars/primary/events",
        headers={"Authorization": f"Bearer {calendar_access_token}"},
        params={"sendUpdates": "none"},
        json=event,
        timeout=30,
    )
    response.raise_for_status()

    created = response.json()
    return {
        "event_id": created["id"],
        "status": created["status"],
        "url": created.get("htmlLink"),
    }


response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=1024,
    tools=tools,
    tool_choice={"type": "auto", "disable_parallel_tool_use": True},
    messages=[
        {
            "role": "user",
            "content": "Schedule a 30-minute sync with ryrl970311@gmail.com on Monday, 19, Oct at 2026, from 01:04 to 01:34 in America/Los_Angeles",
        }
    ],
)

print(f"stop_reason: {response.stop_reason}")

# Show any explanation or clarification question before handling the tool call.
for block in response.content:
    if block.type == "text":
        print(block.text)

# With automatic tool choice, the model may reply without calling a tool.
# Supplying a default prevents next() from raising StopIteration in that case.
tool_use = next(
    (block for block in response.content if block.type == "tool_use"),
    None,
)

if tool_use is None:
    print("No tool call returned. Review the reply above and update the prompt.")
    raise SystemExit(0)

print(f"Tool: {tool_use.name}")
print(f"Input: {tool_use.input}")

# Execute the real calendar API request using the tool's arguments dictionary.
result = create_calendar_event(tool_use.input)
print(json.dumps(result, ensure_ascii=False, indent=2))
