import httpx
from markdownify import markdownify as md
import os
import re

async def browse(url: str) -> str:
    """
    Asynchronicznie pobiera zawartość HTML z podanego URL i konwertuje ją do Markdown.

    Parameters:
    - url (str): The URL to fetch content from.

    Returns:
    - str: The markdown content of the fetched HTML, or an error message if the request fails.
    """
    if url in ["https://aidevs.pl", "https://www.aidevs.pl"]:
        return "You can't browse the main website. Try another URL."

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            html_content = response.text

            # Extract script contents
            script_contents = ""
            script_tags = re.findall(r"<script\b[^>]*>([\s\S]*?)<\/script>", html_content)
            for i, script in enumerate(script_tags, 1):
                script_contents += f"\n\n--- Script {i} ---\n{script}"

            # Convert HTML to markdown using markdownify
            markdown_content = md(html_content)

            # Combine markdown content with script contents
            return f"{markdown_content}\n\n--- Script Contents ---{script_contents}"
    except httpx.RequestError as e:
        print("Error fetching URL:", e)
        return "Failed to fetch the URL, please try again."

async def upload_file(data: dict) -> str:
    """
    Asynchronicznie przesyła plik tekstowy na serwer i zwraca URL pliku.

    Parameters:
    - data (dict): Contains "content" and "file_name" keys.

    Returns:
    - str: The URL of the uploaded file or an error message.
    """
    url = os.getenv("UPLOAD_DOMAIN", "") + "/upload"
    if not url:
        return "ERROR: UPLOAD_DOMAIN environment variable is missing."

    # Sanitize file_name by removing protocol and replacing slashes
    data["file_name"] = data["file_name"].replace("://", "_").replace("/", "_")
    files = {
        'file': (data["file_name"], data["content"], 'text/plain'),
        'file_name': (None, data["file_name"])
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, files=files)
            response.raise_for_status()
            result = response.json()
            return f"Uploaded file to the URL: {result['uploaded_file']}"
    except httpx.RequestError as e:
        print("Upload failed:", e)
        return "Upload failed"

async def play_music(data: dict) -> str:
    """
    Asynchronicznie wysyła żądanie do usługi odtwarzania muzyki.

    Parameters:
    - data (dict): JSON payload for the music service.

    Returns:
    - str: The response from the music service or an error message.
    """
    url = os.getenv("MUSIC_URL", "")
    if not url:
        return "ERROR: MUSIC_URL environment variable is missing."

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            return result.get("data", "Music playback response received")
    except httpx.RequestError as e:
        print("Error playing music:", e)
        return "Failed to play music"

# Dictionary mapping tool names to functions
tools = {
    'get_html_contents': browse,
    'upload_text_file': upload_file,
    'play_music': play_music
}

