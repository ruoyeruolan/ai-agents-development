import os
import anthropic

from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path.home() / ".secrets")

base_url = os.environ.get("ANTHROPIC_BASE_URL")
auth_token = os.environ.get("ANTHROPIC_AUTH_TOKEN")

client = anthropic.Anthropic(base_url=base_url, auth_token=auth_token)
messages = client.messages.create(
    model="deepseek-v4-pro[1m]",
    max_tokens=10240,
    messages=[
        {"role": "user", "content": "Help me respond to this customer service ticket."}
    ],
    tools=[
        {
            "type": "MemSearch",
            "name": "memory",
        }
    ],
)

print(messages)
