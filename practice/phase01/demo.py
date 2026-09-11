import os
import anthropic
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path.home() / ".secrets")

api_key = os.environ.get("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key)

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, world"}],
)
print(message.content)
