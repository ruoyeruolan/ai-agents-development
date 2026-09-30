import os
import anthropic

from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path.home() / ".secrets")

base_url = os.environ.get("ANTHROPIC_BASE_URL")
auth_token = os.environ.get("ANTHROPIC_AUTH_TOKEN")


client = anthropic.Anthropic(base_url=base_url, auth_token=auth_token)
response = client.messages.create(
    model="deepseek-v4-pro[1m]",
    max_tokens=10240,
    messages=[
        {
            "role": "user",
            "content": "What is the weather in San Francisco?",
        }
    ],
    tools=[
        {
            "type": "web_search_20260209",
            "name": "web_search",
        },
        {
            "name": "get_weather",
            "description": "Get the weather at a specific location",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
            "defer_loading": True,
        },
        {
            "name": "search_files",
            "description": "Search through files in the workspace",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "file_types": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["query"],
            },
            "defer_loading": True,
        },
    ],
)

print(response)
