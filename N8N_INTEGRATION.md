# Integracja z n8n

## Jak używać YouTube Transcript Downloader z n8n

### 1. Uruchomienie API

Najpierw uruchom serwer API:

```bash
# Uruchom skrypt startowy
./start_api.sh

# Lub ręcznie:
python3 youtube_transcript_api.py
```

API będzie dostępne na `http://localhost:5000`

### 2. Endpoints

#### Pobieranie transkrypcji
- **URL:** `POST /transcript`
- **Opis:** Główny endpoint do pobierania transkrypcji

**Request Body:**
```json
{
  "video_id": "ABC123xyz",
  "languages": ["pl", "en"],
  "format": "md",
  "translate": null,
  "preserve_formatting": false,
  "exclude_generated": false,
  "exclude_manually_created": false,
  "save_to_file": true,
  "output_dir": "Transcripts",
  "include_metadata": true
}
```

**Response:**
```json
{
  "success": true,
  "video_id": "ABC123xyz",
  "format": "md",
  "metadata": {
    "title": "Tytuł filmu",
    "channel": "Nazwa kanału",
    "views": 1000000,
    "publish_date": "2023-01-01",
    "description": "Opis filmu",
    "url": "https://www.youtube.com/watch?v=ABC123xyz"
  },
  "saved_to": "Transcripts/Tytuł filmu.md",
  "transcript": "# Tytuł filmu\n\n**Kanał:** Nazwa kanału\n\n..."
}
```

#### Listowanie dostępnych transkrypcji
- **URL:** `POST /transcripts/list`
- **Opis:** Pokazuje dostępne języki transkrypcji

**Request Body:**
```json
{
  "video_id": "ABC123xyz"
}
```

#### Pobieranie metadanych
- **URL:** `POST /metadata`
- **Opis:** Pobiera tylko metadane filmu

### 3. Konfiguracja n8n

#### Krok 1: HTTP Request node

1. Dodaj node "HTTP Request"
2. Ustaw metodę na "POST"
3. URL: `http://localhost:5000/transcript`
4. Headers:
   - Content-Type: application/json

#### Krok 2: Body parameters

W sekcji "Body" wybierz "JSON" i dodaj:

```json
{
  "video_id": "{{$json.video_id}}",
  "languages": ["pl", "en"],
  "format": "md",
  "save_to_file": true,
  "include_metadata": true
}
```

#### Krok 3: Przetwarzanie odpowiedzi

Dodaj "Set" node aby przetworzyć odpowiedź:

```javascript
{
  "transcript_text": {{ $json.transcript }},
  "video_title": {{ $json.metadata.title }},
  "channel_name": {{ $json.metadata.channel }},
  "file_path": {{ $json.saved_to }},
  "views": {{ $json.metadata.views }}
}
```

### 4. Przykładowy workflow n8n

#### Workflow 1: Pobieranie transkrypcji z listy ID

1. **Manual Trigger** - Start workflow ręcznie
2. **Set Node** - Ustaw listę video_id
   ```javascript
   {
     "video_ids": ["ABC123", "DEF456", "GHI789"]
   }
   ```
3. **Split In Batches** - Podziel na pojedyncze żądania
4. **HTTP Request** - Wywołaj API dla każdego video_id
5. **Write Binary File** - Zapisz transkrypcję do pliku
6. **Google Sheets** - Zapisz metadane do arkusza

#### Workflow 2: Monitorowanie kanału YouTube

1. **Webhook** - Odbierz powiadomienie o nowym filmie
2. **HTTP Request** - Pobierz transkrypcję
3. **Send Email** - Wyślij email z transkrypcją
4. **Slack** - Powiadom na Slacku

### 5. Przykładowe scenariusze użycia

#### Scenariusz 1: Automatyczna archiwizacja
- Pobierz transkrypcje nowych filmów z określonego kanału
- Zapisz w folderze z datą
- Wygeneruj raport tygodniowy

#### Scenariusz 2: Analiza treści
- Pobierz transkrypcje
- Prześlij do API do analizy sentymentu
- Zapisz wyniki w bazie danych

#### Scenariusz 3: Tłumaczenie
- Pobierz transkrypcję w oryginalnym języku
- Przetłumacz na wiele języków
- Zapisz w różnych folderach

### 6. Error handling

Dodaj "Error Handler" node do obsługi błędów:

```javascript
// Obsługa błędów
if ($response.statusCode !== 200) {
  // Loguj błąd
  // Wyślij powiadomienie
  // Przerwij workflow
}
```

### 7. Optymalizacja

#### Rate limiting
- Dodaj opóźnienie między żądaniami
- Użyj "Wait" node
- Limit: 1 żądanie na 2 sekundy

#### Pamięć podręczna
- Sprawdź czy plik już istnieje
- Pomiń pobieranie jeśli istnieje
- Użyj "IF" node

### 8. Deployment

#### Opcja 1: Local
- Uruchom API na lokalnej maszynie
- Użyj n8n desktop lub cloud

#### Opcja 2: Docker
```bash
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "youtube_transcript_api.py"]
```

#### Opcja 3: Cloud
- Wdróż na Heroku/Render/Vercel
- Użyj environment variables
- Skonfiguruj n8n cloud

### 9. Monitorowanie

Dodaj logging i monitoring:
- Loguj wszystkie żądania
- Monitoruj czas odpowiedzi
- Alerty o błędach

### 10. Bezpieczeństwo

- Dodaj API key
- Użyj HTTPS
- Ogranicz dostęp do endpointów
- Waliduj input data