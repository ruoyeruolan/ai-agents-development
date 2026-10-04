import os
import json
import anthropic

from typing import List
from pathlib import Path
from dotenv import load_dotenv
from anthropic.types.tool_param import ToolParam
from anthropic.types.message_param import MessageParam

load_dotenv(Path.home() / ".secrets")

auth_token = os.environ.get("ANTHROPIC_AUTH_TOKEN")
base_url = os.environ.get("ANTHROPIC_BASE_URL")

client = anthropic.Anthropic(auth_token=auth_token, base_url=base_url)

MAX_OUTPUT_TOKENS = 10240

tools: List[ToolParam] = [
    {
        "name": "create_calendar_event",
        "description": "Create a calender event with attendees and optional recurrence",
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


def run_tool(name, tool_input):
    if name == "create_calendar_event":
        return {
            "event_id": "evt_123",
            "status": "created",
            "title": tool_input["title"],
        }
    return {"error": f"Unknown tool: {name}"}


# Keep the full conversation history in a list so each turn sees prior context.
messages: List[MessageParam] = [
    {
        "role": "user",
        "content": "Schedule a weekly team standup every Monday at 9am (Beijing) for the next 4 weeks. Invite the whole team: ryrl970311@gmail.com, bob@example.com, carol@example.com.",
    }
]

response = client.messages.create(
    model="deepseek-v4-pro[1m]",
    max_tokens=MAX_OUTPUT_TOKENS,
    tools=tools,
    tool_choice={"type": "auto", "disable_parallel_tool_use": True},
    messages=messages,
)

# Loop until Claude stops asking for tools. Each iteration runs the requested
# tool, appends the result to history, and asks Claude to continue.

while response.stop_reason == "tool_use":
    tool_use = next(
        (block for block in response.content if block.type == "tool_use"), None
    )
    if tool_use is None:
        raise RuntimeError("stop_reason=tool_use，但响应中没有 tool_use block")
    result = run_tool(tool_use.name, tool_use.input)

    messages.append({"role": "assistant", "content": response.content})
    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(result),
                }
            ],
        }
    )

    response = client.messages.create(
        model="deepseek-v4-pro[1m]",
        max_tokens=MAX_OUTPUT_TOKENS,
        tools=tools,
        tool_choice={"type": "auto", "disable_parallel_tool_use": True},
        messages=messages,
    )

content_types = [block.type for block in response.content]
print(f"stop_reason: {response.stop_reason}")
print(f"content types: {content_types}")
print(f"output_tokens: {response.usage.output_tokens}")

if response.stop_reason == "max_tokens":
    raise RuntimeError(
        f"模型输出达到上限（{MAX_OUTPUT_TOKENS} tokens），回答尚未完成。"
        "请提高 MAX_OUTPUT_TOKENS 后重试。"
    )

if response.stop_reason != "end_turn":
    raise RuntimeError(f"模型未正常结束：stop_reason={response.stop_reason}")

text_blocks = [block.text for block in response.content if block.type == "text"]
if not text_blocks or not any(text.strip() for text in text_blocks):
    raise RuntimeError(f"模型结束但没有返回有效文本，内容类型：{content_types}")

print("\n".join(text_blocks))
