from index import app
from dotenv import load_dotenv
import os

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv()

# Sprawdź, czy klucz API się załadował
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("Nie znaleziono klucza API w zmiennych środowiskowych lub pliku .env.")

if __name__ == "__main__":
    import uvicorn
    # Uruchom aplikację Quart jako natywną aplikację ASGI
    uvicorn.run("index:app", host="0.0.0.0", port=3000, reload=True)

