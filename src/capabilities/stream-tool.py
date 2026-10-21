from pathlib import Path

import anthropic
from anthropic.types import WebSearchToolRequestErrorParam
from dotenv import load_dotenv

load_dotenv(Path.home() / ".secrets")

tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather in a given location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                }
            },
            "required": ["location"],
        },
    }
]

with anthropic.Anthropic().messages.stream(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "What is the weather like in San Francisco"}],
    tools=tools,
    tool_choice={"type": "any"},
) as stream:
    # for txt in stream.text_stream:
    #     print(txt, end="", flush=True)

    for event in stream:
        print(event.type, event)

    message = stream.get_final_message()
    print("Stop reason: ", message.stop_reason)

    for block in message.content:
        if block.type == "tool_use":
            print("Tool: ", block.name)
            print("Input: ", block.input)
