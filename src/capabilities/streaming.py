from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv(Path.home() / ".secrets")

client = anthropic.Anthropic()

with client.messages.stream(
    max_tokens=256,
    messages=[
        {
            "role": "user",
            "content": "Hello",
        }
    ],
    model="claude-opus-5-5",
) as stream:
    # for txt in stream.text_stream:
    #     print(txt, end="", flush=True)

    for event in stream:
        print(event.type, event)
