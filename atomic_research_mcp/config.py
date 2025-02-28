"""Configuration settings for the Deep Research MCP server."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ChatConfig:
    """Configuration settings for chat models."""

    # OpenAI API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")

    # Default model to use
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        if not cls.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
