from dotenv import load_dotenv
from openai import OpenAI  # type: ignore
from colorama import Fore
import base64
import os

from rich.console import Console  # type: ignore
from rich.pretty import pprint

load_dotenv()

console = Console()

api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    console.print(
        f"[bold cyan]Using API key from .env: {api_key[:8]}...{api_key[-4:]}[/bold cyan]"
    )
else:
    raise ValueError("OPENAI_API_KEY not found in .env file")

client = OpenAI()
console.rule("[bold green]Generating Content with Responses[/bold green]")

response = client.responses.create(
    model="gpt-3.5-turbo",
    input="Write a three-sentence horror story about a vampire.",
    temperature=0.9,
    max_output_tokens=60,
)

pprint(response.output_text)
