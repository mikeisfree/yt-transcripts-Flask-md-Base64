#!/usr/bin/env python3
"""
Skrypt do pobierania transkrypcji z YouTube
"""

import argparse
import sys
import re
import base64
from typing import List, Optional, Dict, Any
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter, JSONFormatter, SRTFormatter, WebVTTFormatter, Formatter
import os
import requests
from bs4 import BeautifulSoup


def get_video_metadata(video_id: str) -> Dict[str, Any]:
    """Pobierz metadane filmu z YouTube"""
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Pobierz tytuł z różnych miejsc
        title = None
        
        # Spróbuj pobrać tytuł z meta tagów
        meta_title = soup.find('meta', property='og:title')
        if meta_title:
            title = meta_title.get('content')
        
        # Jeśli nie znaleziono, spróbuj z innego meta taga
        if not title:
            meta_title = soup.find('meta', name='title')
            if meta_title:
                title = meta_title.get('content')
        
        # Jeśli nadal nie znaleziono, spróbuj z title tag
        if not title:
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text()
                # Usuń " - YouTube" z końca
                title = title.replace(' - YouTube', '').strip()
        
        # Pobierz nazwę kanału
        channel_name = None
        channel_link = soup.find('link', itemprop='name')
        if channel_link:
            channel_name = channel_link.get('content')
        
        # Pobierz liczbę wyświetleń
        views = None
        view_count = soup.find('meta', itemprop='interactionCount')
        if view_count:
            try:
                views = int(view_count.get('content'))
            except (ValueError, TypeError):
                pass
        
        # Pobierz datę publikacji
        publish_date = None
        date_meta = soup.find('meta', itemprop='datePublished')
        if date_meta:
            publish_date = date_meta.get('content')
        
        # Pobierz opis
        description = None
        desc_meta = soup.find('meta', property='og:description')
        if desc_meta:
            description = desc_meta.get('content')
        
        # Pobierz miniaturkę
        thumbnail = None
        thumbnail_meta = soup.find('meta', property='og:image')
        if thumbnail_meta:
            thumbnail = thumbnail_meta.get('content')
        
        return {
            'title': title or f"Video {video_id}",
            'channel': channel_name or "Unknown Channel",
            'views': views,
            'publish_date': publish_date,
            'description': description or "No description available",
            'thumbnail': thumbnail,
            'url': url
        }
        
    except Exception as e:
        print(f"Błąd podczas pobierania metadanych: {e}")
        return {
            'title': f"Video {video_id}",
            'channel': "Unknown Channel",
            'views': None,
            'publish_date': None,
            'description': "No description available",
            'thumbnail': None,
            'url': f"https://www.youtube.com/watch?v={video_id}"
        }


def sanitize_filename(filename: str) -> str:
    """Czyści nazwę pliku z niedozwolonych znaków"""
    # Usuń lub zamień znaki niedozwolone w systemach plików
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Usuń znaki kontrolne
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    
    # Ogranicz długość nazwy pliku
    max_length = 200
    if len(filename) > max_length:
        filename = filename[:max_length].rstrip()
    
    # Usuń białe znaki z początku i końca
    filename = filename.strip()
    
    # Jeśli po czyszczeniu nazwa jest pusta, użyj domyślnej
    if not filename:
        filename = "untitled"
    
    return filename


class MarkdownFormatter(Formatter):
    """Formater do konwersji transkrypcji na format Markdown"""
    
    def format_transcript(self, transcript, **kwargs) -> str:
        """Formatuje transkrypcję do Markdown"""
        if not transcript:
            return ""
        
        content = []
        
        # Pobierz metadane z kwargs
        metadata = kwargs.get('metadata', {})
        
        # Dodaj nagłówek z metadanymi
        if metadata.get('title'):
            content.append(f"# {metadata['title']}\n")
        else:
            content.append("# Transkrypcja filmu\n")
        
        # Dodaj podstawowe informacje
        if metadata.get('channel'):
            content.append(f"**Kanał:** {metadata['channel']}")
        
        if hasattr(transcript, 'video_id'):
            content.append(f"**Video ID:** {transcript.video_id}")
        
        if metadata.get('url'):
            content.append(f"**Link:** {metadata['url']}")
        
        if hasattr(transcript, 'language'):
            content.append(f"**Język transkrypcji:** {transcript.language}")
        
        if hasattr(transcript, 'language_code'):
            content.append(f"**Kod języka:** {transcript.language_code}")
        
        if metadata.get('views'):
            content.append(f"**Wyświetlenia:** {metadata['views']:,}")
        
        if metadata.get('publish_date'):
            content.append(f"**Data publikacji:** {metadata['publish_date']}")
        
        content.append("\n---\n")
        
        # Dodaj opis jeśli dostępny
        if metadata.get('description') and metadata['description'] != "No description available":
            content.append("## Opis")
            content.append(f"{metadata['description']}\n")
            content.append("---\n")
        
        # Formatuj poszczególne segmenty
        content.append("## Transkrypcja\n")
        for snippet in transcript:
            if hasattr(snippet, 'start') and hasattr(snippet, 'duration'):
                timestamp = self._format_timestamp(snippet.start)
                content.append(f"**[{timestamp}]** {snippet.text}")
            else:
                content.append(snippet.text)
        
        return "\n\n".join(content) + "\n"
    
    def format_transcripts(self, transcripts, **kwargs) -> str:
        """Formatuje listę transkrypcji do Markdown"""
        content = []
        for i, transcript in enumerate(transcripts, 1):
            content.append(f"## Transkrypcja {i}")
            content.append(self.format_transcript(transcript, **kwargs))
        
        return "\n".join(content)
    
    def _format_timestamp(self, seconds: float) -> str:
        """Formatuje czas w sekundach do formatu HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"


def get_video_id_from_url(url: str) -> str:
    """Wyodrębnij ID filmu z URL YouTube"""
    if "youtube.com/watch?v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    elif "youtube.com/embed/" in url:
        return url.split("embed/")[1].split("?")[0]
    else:
        return url


def list_available_transcripts(video_id: str) -> None:
    """Wyświetl dostępne transkrypcje dla filmu"""
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
        
        print(f"\nDostępne transkrypcje dla filmu {video_id}:")
        print("-" * 50)
        
        for transcript in transcript_list:
            transcript_type = "Automatyczna" if transcript.is_generated else "Ręczna"
            translatable = "Tak" if transcript.is_translatable else "Nie"
            print(f"Język: {transcript.language} ({transcript.language_code})")
            print(f"Typ: {transcript_type}")
            print(f"Możliwe tłumaczenie: {translatable}")
            if transcript.is_translatable:
                languages = [lang["language_code"] for lang in transcript.translation_languages]
                print(f"Dostępne tłumaczenia: {', '.join(languages[:5])}{'...' if len(languages) > 5 else ''}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Błąd podczas pobierania listy transkrypcji: {e}")


def fetch_transcript(
    video_id: str,
    languages: Optional[List[str]] = None,
    preserve_formatting: bool = False,
    translate_to: Optional[str] = None,
    exclude_generated: bool = False,
    exclude_manually_created: bool = False
) -> str:
    """Pobierz transkrypcję filmu"""
    try:
        ytt_api = YouTubeTranscriptApi()
        
        if languages is None:
            languages = ['pl', 'en']
        
        if exclude_generated and exclude_manually_created:
            raise ValueError("Nie można wykluczyć jednocześnie transkrypcji automatycznych i ręcznych")
        
        if exclude_generated:
            transcript_list = ytt_api.list(video_id)
            transcript = transcript_list.find_manually_created_transcript(languages)
        elif exclude_manually_created:
            transcript_list = ytt_api.list(video_id)
            transcript = transcript_list.find_generated_transcript(languages)
        else:
            transcript = ytt_api.fetch(video_id, languages=languages, preserve_formatting=preserve_formatting)
        
        if translate_to:
            if isinstance(transcript, list):
                raise ValueError("Tłumaczenie nie jest dostępne przy pobieraniu wielu transkrypcji")
            transcript = transcript.translate(translate_to)
        
        if isinstance(transcript, list):
            return transcript[0] if transcript else ""
        else:
            return transcript
            
    except Exception as e:
        print(f"Błąd podczas pobierania transkrypcji: {e}")
        return ""


def encode_to_base64(content: str) -> str:
    """Zakoduj zawartość do base64"""
    try:
        content_bytes = content.encode('utf-8')
        base64_bytes = base64.b64encode(content_bytes)
        return base64_bytes.decode('utf-8')
    except Exception as e:
        print(f"Błąd podczas kodowania base64: {e}")
        return ""


def save_transcript(transcript: str, output_file: str, format_type: str = "text", video_id: str = "", metadata: Dict[str, Any] = None, encode_base64: bool = True) -> None:
    """Zapisz transkrypcję do pliku w wybranym formacie"""
    try:
        if format_type == "json":
            formatter = JSONFormatter()
            formatted_content = formatter.format_transcript(transcript, indent=2)
        elif format_type == "srt":
            formatter = SRTFormatter()
            formatted_content = formatter.format_transcript(transcript)
        elif format_type == "vtt":
            formatter = WebVTTFormatter()
            formatted_content = formatter.format_transcript(transcript)
        elif format_type == "md":
            formatter = MarkdownFormatter()
            # Przekaż metadane do formatera Markdown
            formatted_content = formatter.format_transcript(transcript, metadata=metadata or {})
        else:
            formatter = TextFormatter()
            formatted_content = formatter.format_transcript(transcript)
        
        # Upewnij się, że folder docelowy istnieje
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Zapisz główny plik transkrypcji
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        
        print(f"Transkrypcja została zapisana w pliku: {output_file}")
        
        # Zapisz wersję base64 jeśli format to md i włączono kodowanie
        if format_type == "md" and encode_base64:
            base64_content = encode_to_base64(formatted_content)
            if base64_content:
                base64_file = output_file.replace('.md', '.b64')
                with open(base64_file, 'w', encoding='utf-8') as f:
                    f.write(base64_content)
                print(f"Wersja base64 została zapisana w pliku: {base64_file}")
        
    except Exception as e:
        print(f"Błąd podczas zapisu pliku: {e}")


def main():
    parser = argparse.ArgumentParser(description="Pobierz transkrypcje z YouTube")
    parser.add_argument("video_id", help="ID filmu YouTube lub URL")
    parser.add_argument("--languages", nargs="+", default=["pl", "en"],
                        help="Preferowane języki (domyślnie: pl en)")
    parser.add_argument("--format", choices=["text", "json", "srt", "vtt", "md"],
                        default="md", help="Format wyjściowy (domyślnie: md)")
    parser.add_argument("--output", "-o", help="Nazwa pliku wyjściowego")
    parser.add_argument("--list", action="store_true",
                        help="Wyświetl dostępne transkrypcje")
    parser.add_argument("--translate", help="Przetłumacz na podany język")
    parser.add_argument("--preserve-formatting", action="store_true",
                        help="Zachowaj formatowanie HTML")
    parser.add_argument("--exclude-generated", action="store_true",
                        help="Wyklucz transkrypcje automatyczne")
    parser.add_argument("--exclude-manually-created", action="store_true",
                        help="Wyklucz transkrypcje ręczne")
    parser.add_argument("--no-metadata", action="store_true",
                        help="Nie pobieraj metadanych filmu (tytuł, kanał, etc.)")
    parser.add_argument("--no-base64", action="store_true",
                        help="Nie twórz pliku base64 (domyślnie tworzy dla .md)")
    
    args = parser.parse_args()
    
    video_id = get_video_id_from_url(args.video_id)
    
    if args.list:
        list_available_transcripts(video_id)
        return
    
    # Pobierz metadane filmu
    metadata = {}
    if not args.no_metadata:
        print("Pobieranie metadanych filmu...")
        metadata = get_video_metadata(video_id)
        print(f"Tytuł: {metadata['title']}")
        print(f"Kanał: {metadata['channel']}")
    
    transcript = fetch_transcript(
        video_id=video_id,
        languages=args.languages,
        preserve_formatting=args.preserve_formatting,
        translate_to=args.translate,
        exclude_generated=args.exclude_generated,
        exclude_manually_created=args.exclude_manually_created
    )
    
    if not transcript:
        print("Nie udało się pobrać transkrypcji")
        sys.exit(1)
    
    if args.output:
        save_transcript(transcript, args.output, args.format, video_id, metadata, not args.no_base64)
    else:
        # Domyślnie zapisuj w folderze Transcripts z nazwą pliku zawierającą tytuł
        output_dir = "Transcripts"
        
        if args.format == "md":
            # Użyj tytułu filmu jako nazwy pliku
            safe_title = sanitize_filename(metadata['title'])
            output_file = os.path.join(output_dir, f"{safe_title}.md")
        else:
            # Dla innych formatów użyj video_id
            output_file = os.path.join(output_dir, f"{video_id}.{args.format}")
        
        save_transcript(transcript, output_file, args.format, video_id, metadata, not args.no_base64)


if __name__ == "__main__":
    main()