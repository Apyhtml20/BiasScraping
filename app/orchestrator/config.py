import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv(Path(__file__).parent / ".env")


class LLMConfig:
    def __init__(self):
        self.api_key = os.getenv("NVIDIA_API_KEY")
        self.base_url = "https://integrate.api.nvidia.com/v1"
        self.model = "nvidia/nemotron-3-nano-30b-a3b"

        if not self.api_key:
            raise ValueError(
                "NVIDIA_API_KEY is not configured."
            )

    def create_client(self) -> OpenAI:
        return OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )