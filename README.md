# 🎥 YouTube Transcripts Downloader

Advanced tool for downloading YouTube video transcripts with metadata support and n8n integration.

Project inspired by [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)

## ✨ Features

- 📝 **Rich metadata** - video titles, channel names, view counts, description
- 🎯 **Smart naming** - files named using video titles
- 🌐 **Multiple formats** - Markdown, JSON, SRT, VTT, plain text
- 🚀 **n8n integration** - full API server for workflow automation
- 🛡️ **Error handling** - robust error handling and validation
- 🌍 **Multi-language** - support for multiple transcript languages
- 🔄 **Translation** - automatic transcript translation
- 📁 **Auto-organization** - automatic file organization in Transcripts/ folder
- 🔐 **Base64 encoding** - automatyczne kodowanie base64 dla plików .md
- 🤖 **AI Notes Agent** - automatyczne generowanie profesjonalnych notatek (Gemini AI)
- 📝 **Style notatek** - wybór między stylem ciągłym a punktowanym
- ✅ **Checklisty** - generowanie listy zadań i tematów do zapamiętania

## 📋 Prerequisites

- Python 3.6+
- pip package manager
- (Optional) n8n for workflow automation

## 🚀 Quick Start

### Option 1: CLI Usage

```bash
# Clone repo
git clone https://github.com/mikeisfree/yt-transcripts-Flask-md-Base64.git

# Go to repo
cd yt-transcripts-Flask-md-Base64

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate

# MS Windows:
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download transcript (uses video title as filename)
python youtube_transcript_downloader.py ABC123xyz

# (OPTIONAL) Specify language and format
python youtube_transcript_downloader.py ABC123xyz --languages pl --format json
```

### Option 2: API Server (for n8n)

```bash
# Start API server
./start_api.sh

# Or manually
python api_server.py
```

API will be available at `http://localhost:5000`

## 📁 Struktura projektu

```
yt-transcripts/
├── youtube_transcript_downloader.py  # Główny skrypt CLI
├── api_server.py                     # API server dla n8n
├── start_api.sh                      # Skrypt startowy API
├── requirements.txt                  # Zależności
├── Transcripts/                      # Folder z transkrypcjami
├── README.md                         # Dokumentacja
├── N8N_INTEGRATION.md               # Szczegółowa dokumentacja n8n
├── LICENSE                           # Licencja MIT
└── .gitignore                       # Pliki ignorowane przez Git
```

---

## 🔧 CLI Tool

## Python Script

### YouTube Transcript Downloader

Skrypt do pobierania transkrypcji z YouTube oparty na bibliotece `youtube-transcript-api`.

#### Instalacja

1. Zainstaluj wymagane zależności:

```bash
pip install youtube-transcript-api
```

2. Nadaj uprawnienia wykonawcze skryptowi:

```bash
chmod +x youtube_transcript_downloader.py
```

#### Użycie

**Podstawowe użycie:**

```bash
# Pobierz transkrypcję po ID filmu
python youtube_transcript_downloader.py ABC123xyz

# Lub użyj pełnego URL
python youtube_transcript_downloader.py "https://www.youtube.com/watch?v=ABC123xyz"
```

**Opcje językowe:**

```bash
# Określ preferowane języki
python youtube_transcript_downloader.py ABC123xyz --languages pl en de

# Przetłumacz transkrypcję
python youtube_transcript_downloader.py ABC123xyz --translate de
```

**Formaty wyjściowe:**

```bash
# Zapisz w formacie JSON
python youtube_transcript_downloader.py ABC123xyz --format json --output transcript.json

# Zapisz w formacie SRT
python youtube_transcript_downloader.py ABC123xyz --format srt --output transcript.srt

# Zapisz w formacie VTT
python youtube_transcript_downloader.py ABC123xyz --format vtt --output transcript.vtt

# Zapisz w formacie Markdown (domyślnie)
python youtube_transcript_downloader.py ABC123xyz

# Zapisz jako czysty tekst
python youtube_transcript_downloader.py ABC123xyz --format text --output transcript.txt
```

**Inne opcje:**

```bash
# Wyświetl dostępne transkrypcje
python youtube_transcript_downloader.py ABC123xyz --list

# Zachowaj formatowanie HTML
python youtube_transcript_downloader.py ABC123xyz --preserve-formatting

# Wyklucz transkrypcje automatyczne
python youtube_transcript_downloader.py ABC123xyz --exclude-generated

# Wyklucz transkrypcje ręczne
python youtube_transcript_downloader.py ABC123xyz --exclude-manually-created
```

#### Przykłady

1. **Pobierz transkrypcję w formacie Markdown (domyślnie):**

```bash
python youtube_transcript_downloader.py ABC123xyz
```

Pliki zostaną zapisane jako `Transcripts/Tytuł Filmu.md` i `Transcripts/Tytuł Filmu.b64`

2. **Pobierz transkrypcję bez kodowania base64:**

```bash
python youtube_transcript_downloader.py ABC123xyz --no-base64
```

3. **Pobierz polską transkrypcję i zapisz do pliku:**

```bash
python youtube_transcript_downloader.py ABC123xyz --languages pl --output transcript.md
```

4. **Pobierz transkrypcję w formacie SRT:**

```bash
python youtube_transcript_downloader.py ABC123xyz --format srt --output subtitles.srt
```

5. **Sprawdź dostępne języki transkrypcji:**

```bash
python youtube_transcript_downloader.py ABC123xyz --list
```

6. **Przetłumacz transkrypcję na niemiecki:**

```bash
python youtube_transcript_downloader.py ABC123xyz --languages en --translate de
```

7. **Pobierz transkrypcję z zachowaniem formatowania HTML:**

```bash
python youtube_transcript_downloader.py ABC123xyz --preserve-formatting
```

---

## 🤖 AI Notes Agent

Nowa funkcjonalność pozwala na automatyczne generowanie inteligentnych notatek z pobranej transkrypcji przy użyciu **Google Gemini AI**.

### Funkcje Agenta:
- **Dwa style notatek**:
  - `(a) Ciągła`: Spójny opis z podziałem na sekcje tematyczne i wnioskami.
  - `(b) Punktowana`: Zwięzłe opisy sekcji uzupełnione listami punktowanymi.
- **Checklista**: Możliwość dodania na końcu sekcji z zadaniami do wykonania i tematami do zapamiętania.
- **Wsparcie dla języków**: Agent tworzy notatki w języku, w którym pobrana została transkrypcja.
- **Inteligentne formatowanie**: Markdown z nagłówkami, pogrubieniami i cytatami.

### Użycie (CLI):
Po pobraniu transkrypcji skrypt zapyta interaktywnie:
1. Czy utworzyć notatki? (y/n)
2. Wybór typu (Ciągła/Punktowana)
3. Czy dodać checklistę? (y/n)

Notatki zostaną zapisane w pliku `{Tytuł Filmu}-notes.md` w folderze `Transcripts/`.

### Konfiguracja API Gemini:
- Skrypt wymaga klucza API Gemini. Możesz go uzyskać bezpłatnie na: [Google AI Studio](https://aistudio.google.com/apikey).
- Przy pierwszym uruchomieniu skrypt poprosi o podanie klucza i zapisze go w pliku `.env`.
- Możesz pominąć powiadomienie o notatkach używając flagi `--no-notes`.

---

#### Struktura plików

```
yt-transcripts/
├── youtube_transcript_downloader.py
├── Transcripts/
│   ├── ABC123xyz.md
│   └── DEF456uvw.json
└── README.md
```

#### Format Markdown

Transkrypcje zapisane w formacie Markdown zawierają:

- Nagłówek z informacjami o filmie (ID, język)
- Znaczniki czasowe w formacie `[MM:SS]` lub `[HH:MM:SS]`
- Czytelny podział na akapity

#### Base64 Encoding

Dla każdego pliku `.md` tworzony jest dodatkowo plik `.b64` zawierający:

- Zawartość transkrypcji zakodowaną w base64
- Może być używany do bezpiecznego transferu danych
- Przydatny w integracjach z systemami zewnętrznymi
- Można wyłączyć za pomocą flagi `--no-base64`

#### Ograniczenia

- Niektóre filmy mogą mieć zablokowany dostęp do transkrypcji
- Filmy z ograniczeniami wiekowymi mogą wymagać dodatkowego uwierzytelnienia
- YouTube może blokować zbyt częste żądania z tego samego IP

---

## 🌐 n8n Integration

The project includes a full API server for seamless integration with n8n workflows.

### Quick Setup

1. **Start the API server:**

```bash
./start_api.sh
```

2. **Test the API:**

```bash
curl -X POST http://localhost:5000/transcript \
  -H "Content-Type: application/json" \
  -d '{"video_id": "ABC123xyz"}'
```

### API Endpoints

| Endpoint            | Method | Description              |
| ------------------- | ------ | ------------------------ |
| `/transcript`       | POST   | Main transcript download |
| `/transcripts/list` | POST   | List available languages |
| `/metadata`         | POST   | Get video metadata only  |
| `/health`           | GET    | Health check             |

### Example API Request

```bash
curl -X POST http://localhost:5000/transcript \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "ABC123xyz",
    "languages": ["pl", "en"],
    "format": "md",
    "save_to_file": true,
    "include_metadata": true
  }'
```

### Example Response

```json
{
  "success": true,
  "video_id": "ABC123xyz",
  "format": "md",
  "metadata": {
    "title": "Video Title",
    "channel": "Channel Name",
    "views": 1000000,
    "publish_date": "2023-01-01",
    "description": "Video description",
    "url": "https://www.youtube.com/watch?v=ABC123xyz"
  },
  "saved_to": "Transcripts/Video Title.md",
  "base64_file": "Transcripts/Video Title.b64",
  "base64": "IyBWaWRlbyBUaXRsZQ0KDQoqKkthbmFsOioqIENoYW5uZWwgTmFtZQ0KKiZWlkZW8gSUQ6KiogQUJDMTIzeHl6DQoqKkxpbms6KiogaHR0cHM6Ly93d3cueW91dHViZS5jb20vd2F0Y2g/dj1BQkMxMjN4eXoNCioqSmV6eWsgdHJhbnNrcmlwY2ppOioqIHBsDQoqKktvZCBqZXp5a3U6KiogZW4NCioqRGF0YSBwdWJsaWthY2ppOioqIDIwMjMtMDEtMDENCioqV3lzdGVwZW5pYToqKiAxLDAwMCwwMDANCg0KLS0tDQoNCiMjIE9waXMNCk9waXMgZmlsbXUuLi4NCg0KLS0tDQoNCiMjIFRyYW5za3JpcGNqYQ0KKipbMDA6MDBdKiogV2l0YWogc3dpZXRhIMWCYXJkb25hISEuLi4=",
  "transcript": "# Video Title\n\n**Kanał:** Channel Name\n\n..."
}
```

### n8n Workflow Setup

1. **Add HTTP Request Node:**
   - Method: POST
   - URL: `http://localhost:5000/transcript`
   - Headers: `Content-Type: application/json`
   - Body (JSON):
     ```json
     {
       "video_id": "{{$json.video_id}}",
       "languages": ["pl", "en"],
       "format": "md",
       "save_to_file": true,
       "encode_base64": true
     }
     ```

2. **Process Response:**
   Add a Set node to extract data:
   ```javascript
   {
     "transcript_text": {{ $json.transcript }},
     "video_title": {{ $json.metadata.title }},
     "channel_name": {{ $json.metadata.channel }},
     "file_path": {{ $json.saved_to }},
     "base64_file": {{ $json.base64_file }},
     "base64_content": {{ $json.base64 }},
     "views": {{ $json.metadata.views }}
   }
   ```

### Sample n8n Workflows

#### Workflow 1: Automated Transcript Collection

```
Trigger (Schedule) →
Google Sheets (Get video IDs) →
HTTP Request (Our API) →
Set (Process data) →
Google Sheets (Save results)
```

#### Workflow 2: Content Analysis

```
Webhook (New video) →
HTTP Request (Get transcript) →
AI Service (Analyze) →
Slack (Send notification)
```

### Advanced Features

- **Rate limiting ready** - built for high-volume processing
- **Error handling** - comprehensive error responses
- **Metadata extraction** - rich video information
- **File auto-save** - automatic file organization
- **Multiple formats** - support for various output formats
- **Base64 encoding** - automatic base64 encoding for secure data transfer

For detailed integration examples, see [N8N_INTEGRATION.md](N8N_INTEGRATION.md).

---

## 📦 Installation

### Requirements

```bash
# Install Python dependencies
pip install -r requirements.txt

# Make scripts executable
chmod +x start_api.sh
chmod +x youtube_transcript_downloader.py
```

### Docker Setup (Optional)

```bash
# Build and run with Docker
docker build -t youtube-transcripts .
docker run -p 5000:5000 youtube-transcripts
```

---

## 🛠️ Development

### Testing the Application

```bash
# Run functionality tests
python test_functionality.py

# Run CLI tests
python youtube_transcript_downloader.py --help

# Test API endpoints
curl http://localhost:5000/health
```

### Environment Variables

| Variable     | Default     | Description       |
| ------------ | ----------- | ----------------- |
| `PORT`       | 5000        | API server port   |
| `DEBUG`      | false       | Enable debug mode |
| `OUTPUT_DIR` | Transcripts | Output directory  |

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## 📞 Support

For issues and questions:

- Create an issue on GitHub
- Check the [N8N_INTEGRATION.md](N8N_INTEGRATION.md) for n8n-specific help

---

## Go CLI Tool

```
Usage off: yt-transcripts: [COMMAND] [OPTIONS]

Commands:
  save    Save the transcript to the specified file path.
  list    List available video transcripts.
  fetch   Fetch the transcript.

Options:
  --help, -h      Display command help message.
  --version, -v   Show app version.
```

```
Usage of: yt-transcripts list [OPTIONS]

Options:
  -i, --id          Video ID
```

```
Usage of: yt-transcripts save [OPTIONS]

Options:
  -i, --id          Video ID
  -l, --language    Language code in which you want to store the transcript
  -o, --output      Filename in which the data will be stored
```

```
Usage of: yt-transcripts fetch [OPTIONS]

Options:
  -i, --id          Video ID
  -l, --language    Language code in which you want to search for the transcript
```
