#!/usr/bin/env python3
"""
API dla YouTube Transcript Downloader - do integracji z n8n
"""

import json
import os
import sys
from flask import Flask, request, jsonify
from youtube_transcript_downloader import (
    get_video_id_from_url,
    get_video_metadata,
    fetch_transcript,
    save_transcript,
    MarkdownFormatter,
    sanitize_filename,
    encode_to_base64
)

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "youtube-transcript-api"})

@app.route('/transcript', methods=['POST'])
def get_transcript():
    """Główny endpoint do pobierania transkrypcji"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Brak danych wejściowych"}), 400
        
        video_id_or_url = data.get('video_id') or data.get('url')
        if not video_id_or_url:
            return jsonify({"error": "Brak video_id lub url"}), 400
        
        # Ekstrakcja video_id
        video_id = get_video_id_from_url(video_id_or_url)
        
        # Parametry opcjonalne
        languages = data.get('languages', ['pl', 'en'])
        format_type = data.get('format', 'md')
        translate_to = data.get('translate')
        preserve_formatting = data.get('preserve_formatting', False)
        exclude_generated = data.get('exclude_generated', False)
        exclude_manually_created = data.get('exclude_manually_created', False)
        save_to_file = data.get('save_to_file', True)
        output_dir = data.get('output_dir', 'Transcripts')
        include_metadata = data.get('include_metadata', True)
        encode_base64 = data.get('encode_base64', True)
        
        # Pobierz metadane jeśli wymagane
        metadata = {}
        if include_metadata:
            metadata = get_video_metadata(video_id)
        
        # Pobierz transkrypcję
        transcript = fetch_transcript(
            video_id=video_id,
            languages=languages,
            preserve_formatting=preserve_formatting,
            translate_to=translate_to,
            exclude_generated=exclude_generated,
            exclude_manually_created=exclude_manually_created
        )
        
        if not transcript:
            return jsonify({"error": "Nie udało się pobrać transkrypcji"}), 404
        
        # Przygotuj wynik
        result = {
            "success": True,
            "video_id": video_id,
            "format": format_type,
            "transcript": None,
            "base64": None
        }
        
        # Dodaj metadane jeśli dostępne
        if metadata:
            result["metadata"] = metadata
        
        # Zapisz do pliku jeśli wymagane
        if save_to_file:
            os.makedirs(output_dir, exist_ok=True)
            
            if format_type == 'md' and metadata.get('title'):
                safe_title = sanitize_filename(metadata['title'])
                output_file = os.path.join(output_dir, f"{safe_title}.{format_type}")
            else:
                output_file = os.path.join(output_dir, f"{video_id}.{format_type}")
            
            save_transcript(transcript, output_file, format_type, video_id, metadata, encode_base64)
            result["saved_to"] = output_file
            
            # Dodaj ścieżkę do pliku base64 jeśli został utworzony
            if encode_base64 and format_type == 'md':
                base64_file = output_file.replace('.md', '.b64')
                if os.path.exists(base64_file):
                    result["base64_file"] = base64_file
                    
                    # Odczytaj zawartość base64 dla odpowiedzi API
                    try:
                        with open(base64_file, 'r', encoding='utf-8') as f:
                            result["base64"] = f.read()
                    except Exception as e:
                        print(f"Błąd podczas odczytu pliku base64: {e}")
        
        # Formatuj transkrypcję do odpowiedzi
        if format_type == 'json':
            formatter = MarkdownFormatter()
            result["transcript"] = formatter.format_transcript(transcript, metadata=metadata)
        elif format_type == 'raw':
            # Surowe dane transkrypcji
            result["transcript"] = transcript.to_raw_data() if hasattr(transcript, 'to_raw_data') else str(transcript)
        else:
            # Formatuj do tekstowej formy
            if format_type == 'md':
                formatter = MarkdownFormatter()
                result["transcript"] = formatter.format_transcript(transcript, metadata=metadata)
            else:
                from youtube_transcript_api.formatters import TextFormatter
                formatter = TextFormatter()
                result["transcript"] = formatter.format_transcript(transcript)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/transcripts/list', methods=['POST'])
def list_transcripts():
    """Endpoint do listowania dostępnych transkrypcji"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Brak danych wejściowych"}), 400
        
        video_id_or_url = data.get('video_id') or data.get('url')
        if not video_id_or_url:
            return jsonify({"error": "Brak video_id lub url"}), 400
        
        video_id = get_video_id_from_url(video_id_or_url)
        
        from youtube_transcript_api import YouTubeTranscriptApi
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
        
        transcripts_info = []
        for transcript in transcript_list:
            transcripts_info.append({
                "language": transcript.language,
                "language_code": transcript.language_code,
                "is_generated": transcript.is_generated,
                "is_translatable": transcript.is_translatable,
                "translation_languages": transcript.translation_languages
            })
        
        return jsonify({
            "success": True,
            "video_id": video_id,
            "available_transcripts": transcripts_info
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/metadata', methods=['POST'])
def get_video_info():
    """Endpoint do pobierania metadanych filmu"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Brak danych wejściowych"}), 400
        
        video_id_or_url = data.get('video_id') or data.get('url')
        if not video_id_or_url:
            return jsonify({"error": "Brak video_id lub url"}), 400
        
        video_id = get_video_id_from_url(video_id_or_url)
        metadata = get_video_metadata(video_id)
        
        return jsonify({
            "success": True,
            "video_id": video_id,
            "metadata": metadata
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Uruchom serwer
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"Uruchamianie YouTube Transcript API na porcie {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)