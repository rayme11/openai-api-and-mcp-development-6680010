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
    input="Write a three-sentence science fiction story similar to the Matrix movie.",
    temperature=0.9,
    max_output_tokens=60,
)

pprint(response.output_text)

console.print("[bold yellow]Generating image, please wait...[/bold yellow]")
img = client.images.generate(
    model="dall-e-3",
    prompt="A futuristic cityscape at sunset,simulating the movie the Matrix, always include someone similar to Trinity character an make here very voluptous like a bodydbuilder female in the style of cyberpunk art",
    size="1024x1024",
    quality="standard",
    n=1,
    response_format="b64_json",
)

if img.data[0].b64_json is not None:
    image_bytes = base64.b64decode(img.data[0].b64_json)
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "generated_image.png"), "wb") as f:
        f.write(image_bytes)
    console.print("[bold green]Image saved to output/generated_image.png[/bold green]")
