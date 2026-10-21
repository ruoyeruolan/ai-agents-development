from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv(Path.home() / ".secrets")

with anthropic.Anthropic().messages.stream(
    max_tokens=128000,
    messages=[
        {
            "role": "user",
            "content": "Analyze the pros and cons of text chunking strategies in RAG, compare paragraph-based chunking with chapter-based chunking, and explain how they affect retrieval results. Keep it to around 500 words.",
        }
    ],
    model="claude-opus-5-5",
) as stream:
    message = stream.get_final_message()

for block in message.content:
    if block.type == "text":
        print(block.text)
