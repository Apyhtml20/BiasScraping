import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class LLMConfig:
    def __init__(self):
        self.api_key = os.getenv("NVIDIA_API_KEY")
        self.base_url = "https://integrate.api.nvidia.com/v1"
        self.model = "openai/gpt-oss-20b"

        if not self.api_key:
            raise ValueError(
                "NVIDIA_API_KEY is not configured."
            )

    def create_client(self) -> OpenAI:
        return OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )