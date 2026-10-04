import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv(Path.home() / ".secrets")
base_url = os.environ.get("ANTHROPIC_BASE_URL")
auth_token = os.environ.get("ANTHROPIC_AUTH_TOKEN")

client = anthropic.Anthropic(
    base_url=base_url,
    auth_token=auth_token,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = PROJECT_ROOT / "plans" / "ai-agent-development-roadmap.md"
