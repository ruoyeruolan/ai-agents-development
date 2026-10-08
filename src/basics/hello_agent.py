# import os
import anthropic
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path.home() / ".secrets")

# api_key = os.environ.get("ANTHROPIC_API_KEY")

message = anthropic.Anthropic().messages.create(
    model="claude-haiku-5-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, introduce yourself"}],
)
# print(message.content)

for block in message.content:
    if block.type == "text":
        print(block.text)
