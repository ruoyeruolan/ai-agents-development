# Ring 3: Multiple tools, parallel calls.

import os
import json
import anthropic

from typing import List
from pathlib import Path
from dotenv import load_dotenv
from anthropic.types import Message, MessageParam, ToolParam, ToolResultBlockParam

MAX_TOKEN = 10240

load_dotenv(Path.home() / ".secrets")

base_url = os.environ.get("ANTHROPIC_BASE_URL")
auth_token = os.environ.get("ANTHROPIC_AUTH_TOKEN")

client = anthropic.Anthropic(auth_token=auth_token, base_url=base_url)

tools: List[ToolParam] = [
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
    },
    {
        "name": "list_calendar_events",
        "description": "List all calendar events on a given date.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "format": "date"},
            },
            "required": ["date"],
        },
    },
]


def run_tool(name, tool_input):
    if name == "create_calendar_event":
        if "attendees" in tool_input and len(tool_input["attendees"]) > 10:
            raise ValueError("Too many attendees (max 10)")
        return {
            "event_id": "evt_123",
            "status": "created",
            "title": tool_input["title"],
        }
    if name == "list_calendar_events":
        return {
            "events": [{"title": "Existing meeting", "start": "14:00", "end": "15:00"}]
        }
    return ValueError(f"Unknown tool: {name}")


def log_response(response: Message, turn: int):
    print(f"[Turn {turn}] Response received", flush=True)
    print(f"  Stop reason: {response.stop_reason}", flush=True)
    print(f"  Content types: {[block.type for block in response.content]}", flush=True)
    print(f"  Output tokens: {response.usage.output_tokens}", flush=True)
    print(
        f"  Tool calls: {sum(block.type == 'tool_use' for block in response.content)}",
        flush=True,
    )


messages: List[MessageParam] = [
    {
        "role": "user",
        "content": "Check what I have next Monday, then schedule a planning session that avoids any conflicts.",
    }
]

turn = 1
print("Starting agent loop. Calendar tools return simulated results.", flush=True)
print(f"[Turn {turn}] Requesting model response...", flush=True)
response = client.messages.create(
    model="deepseek-v4-pro[1m]",
    max_tokens=MAX_TOKEN,
    tools=tools,
    messages=messages,
)
log_response(response, turn)

while response.stop_reason == "tool_use":
    # A single response can contain multiple tool_use blocks. Process all of
    # them and return all results together in one user message.
    tool_results: List[ToolResultBlockParam] = []
    for block in response.content:
        if block.type == "tool_use":
            try:
                print(
                    f"[Turn {turn}] Running tool: {block.name} (id={block.id})",
                    flush=True,
                )
                print(
                    f"  Input: {json.dumps(block.input, ensure_ascii=False)}",
                    flush=True,
                )
                result = run_tool(block.name, block.input)
                print(f"  Result: {json.dumps(result, ensure_ascii=False)}", flush=True)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                    }
                )
            except Exception as exc:
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(exc),
                        "is_error": True,
                    }
                )

    if not tool_results:
        raise RuntimeError("The model reported tool_use but returned no tool calls.")

    messages.append({"role": "assistant", "content": response.content})
    messages.append({"role": "user", "content": tool_results})

    print(
        f"[Turn {turn}] Returning {len(tool_results)} tool result(s) to the model.",
        flush=True,
    )
    turn += 1
    print(f"[Turn {turn}] Requesting model response...", flush=True)
    response = client.messages.create(
        model="deepseek-v4-pro[1m]",
        max_tokens=MAX_TOKEN,
        tools=tools,
        messages=messages,
    )
    log_response(response, turn)


if response.stop_reason != "end_turn":
    raise RuntimeError(
        f"The model did not finish normally (stop_reason={response.stop_reason}). "
        "If the token limit was reached, increase MAX_TOKEN and try again."
    )

text_blocks = [block.text for block in response.content if block.type == "text"]
if not any(text.strip() for text in text_blocks):
    raise RuntimeError("The model ended its turn without returning any text.")

print(f"Agent loop finished after {turn} model request(s).", flush=True)
print("Final response:", flush=True)
print("\n".join(text_blocks), flush=True)
