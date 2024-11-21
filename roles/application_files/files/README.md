
# AI Dev Agent

AI Dev Agent to projekt, który umożliwia interakcję z modelem AI w celu realizacji określonych zadań. Projekt ten wykorzystuje różne narzędzia do przetwarzania tekstu oraz integrację z modelem Anthropic Claude. Jest skonfigurowany do działania jako serwer aplikacji Flask, który udostępnia kilka endpointów do obsługi żądań użytkownika.

## Konfiguracja

Aby skonfigurować projekt, upewnij się, że masz skonfigurowane następujące zmienne środowiskowe:

- `UPLOAD_DOMAIN`: URL domeny, na której pliki będą hostowane.
- `ANTHROPIC_API_KEY`: Klucz API dla integracji z Anthropic API.

## Użycie

Uruchomienie serwera aplikacji odbywa się poprzez aktywację środowiska wirtualnego i wykonanie skryptu `index.py`. Serwer działa na `http://localhost:3000`.

Dostępne endpointy to m.in.:

- `/`: Główny endpoint do przetwarzania żądań.
- `/upload`: Endpoint do przesyłania plików tekstowych.
- `/task`: Endpoint do wykonywania zadań zdefiniowanych w `TaskManager`.
- `/ssh_command`: Endpoint do wykonywania poleceń SSH zdefiniowanych w `AsyncSSHManager`.

## Struktura katalogów

- `lib/`: Katalog zawierający moduły agenta, takie jak AI, narzędzia, i prompty.
- `uploads/`: Katalog do przechowywania przesłanych plików.
- `log.md`: Plik do rejestrowania operacji agenta.
