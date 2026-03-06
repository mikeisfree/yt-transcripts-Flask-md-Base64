#!/usr/bin/env python3
"""
Agent do generowania notatek z transkrypcji YouTube za pomocą Gemini API.
"""

import os
import sys
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
except ImportError:
    print("❌ Brak pakietu python-dotenv. Zainstaluj: pip install python-dotenv")
    sys.exit(1)


# ─── API Key Management ────────────────────────────────────────────────────────

def _get_env_path() -> Path:
    """Zwraca bezwzględną ścieżkę do pliku .env w katalogu projektu."""
    return Path(__file__).resolve().parent / '.env'


def check_api_key() -> Optional[str]:
    """
    Sprawdza dostępność klucza API Gemini.
    Jeśli brak — prosi użytkownika o podanie i zapisuje w .env.
    """
    env_path = _get_env_path()
    
    # Wymuś załadowanie z konkretnej ścieżki
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=True)
    
    api_key = os.getenv('GEMINI_API_KEY')

    if api_key:
        return api_key

    print("\n⚠️  Brak klucza API Gemini.")
    print("Aby korzystać z generowania notatek, potrzebujesz klucza API Google Gemini.")
    print("Możesz go uzyskać na: https://aistudio.google.com/apikey\n")

    api_key = input("Podaj klucz API Gemini: ").strip()

    if not api_key:
        print("❌ Nie podano klucza API. Pomijam generowanie notatek.")
        return None

    # Zapisz/Aktualizuj w .env
    lines = []
    if env_path.exists():
        with open(env_path, 'r') as f:
            lines = f.readlines()
    
    # Usuń stare wpisy klucza
    lines = [line for line in lines if not line.startswith('GEMINI_API_KEY=')]
    lines.append(f"GEMINI_API_KEY={api_key}\n")

    with open(env_path, 'w') as f:
        f.writelines(lines)

    print(f"✅ Klucz API zapisany w {env_path}")
    os.environ['GEMINI_API_KEY'] = api_key
    return api_key


def verify_api_connection(api_key: str) -> bool:
    """Weryfikuje czy klucz API działa przez szybkie zapytanie testowe."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Respond with only: OK")
        return bool(response.text)
    except Exception as e:
        print(f"❌ Błąd połączenia z API Gemini: {e}")
        return False


# ─── Prompt Building ───────────────────────────────────────────────────────────

STYLE_CONTINUOUS = """
## Styl notatki: CIĄGŁY
- Podziel notatki na sekcje tematyczne
- Każda sekcja powinna mieć nagłówek (## lub ###)
- Treść w formie spójnego, ciągłego opisu
- Skup się na najważniejszych treściach, wnioskach i kluczowych informacjach
- Zachowaj logiczną strukturę i płynność tekstu
- Unikaj powtórzeń i wypełniaczy
"""

STYLE_BULLET = """
## Styl notatki: PUNKTOWANA
- Podziel notatki na sekcje tematyczne
- Każda sekcja powinna mieć nagłówek (## lub ###)
- Pod nagłówkiem krótki opis sekcji (1-2 zdania)
- Dalsze treści przedstaw w formie listy punktowanej (-)
- Każdy punkt powinien być zwięzły i konkretny
- Nie powtarzaj treści z opisu sekcji w punktach
"""

CHECKLIST_INSTRUCTION = """
## Checklista
- Na końcu notatki dodaj sekcję "## ✅ Checklista"
- Użyj formatu checklisty markdown: - [ ] element
- Uwzględnij najważniejsze zadania do wykonania, jeśli takie się pojawiły w transkrypcji
- Dodaj tematy do przemyślenia lub zapamiętania
- Dodaj kluczowe wnioski do zapamiętania
- Jeśli nie ma konkretnych zadań, dodaj najważniejsze takeaway'e do zapamiętania
"""


def build_prompt(transcript_content: str, note_type: str, include_checklist: bool) -> str:
    """Buduje prompt dla Gemini na podstawie wybranego typu notatki."""

    style = STYLE_CONTINUOUS if note_type == 'continuous' else STYLE_BULLET
    checklist = CHECKLIST_INSTRUCTION if include_checklist else ""

    prompt = f"""Jesteś ekspertem w tworzeniu zwięzłych, wartościowych notatek z transkrypcji wideo.

## Zadanie
Na podstawie poniższej transkrypcji wideo utwórz szczegółowe notatki.

{style}

{checklist}

## Formatowanie
- Używaj formatowania Markdown
- Nagłówek H1 (#) z tytułem notatki (użyj tytułu wideo z transkrypcji)
- Sekcje z nagłówkami H2 (##) lub H3 (###)
- Wyróżniaj kluczowe pojęcia **pogrubieniem**
- Linki i odniesienia zachowaj jeśli się pojawiły w transkrypcji
- Używaj cytatów (>) dla szczególnie ważnych wypowiedzi

## Wytyczne
- Pisz w tym samym języku co transkrypcja
- Skup się na meritum — pomijaj wątki poboczne, powtórzenia i wypełniacze
- Zachowaj wszystkie ważne fakty, liczby, nazwy własne
- Notatki powinny być samodzielnym źródłem wiedzy — czytelnik nie musi oglądać wideo
- Nie dodawaj informacji od siebie, bazuj wyłącznie na transkrypcji

---

## Transkrypcja:

{transcript_content}"""

    return prompt


# ─── Notes Generation ──────────────────────────────────────────────────────────

def generate_notes(
    transcript_content: str,
    note_type: str,
    include_checklist: bool,
    output_path: str
) -> bool:
    """
    Generuje notatki z transkrypcji za pomocą Gemini API i zapisuje do pliku.

    Args:
        transcript_content: Treść transkrypcji (pełny Markdown)
        note_type: 'continuous' lub 'bullet'
        include_checklist: Czy dodać checklistę na końcu
        output_path: Ścieżka do pliku wyjściowego

    Returns:
        True jeśli udało się wygenerować notatki, False w przeciwnym wypadku
    """
    # 1. Sprawdź klucz API
    api_key = check_api_key()
    if not api_key:
        return False

    # 2. Import Gemini SDK
    try:
        import google.generativeai as genai
    except ImportError:
        print("❌ Brak pakietu google-generativeai.")
        print("   Zainstaluj: pip install google-generativeai")
        return False

    # 3. Weryfikacja połączenia
    print("\n🔄 Weryfikacja połączenia z API Gemini...")
    genai.configure(api_key=api_key)

    if not verify_api_connection(api_key):
        # Może klucz jest nieprawidłowy — daj szansę na podanie nowego
        print("Klucz API może być nieprawidłowy.")
        retry = input("Podać nowy klucz API? (y/n): ").strip().lower()
        if retry == 'y':
            new_key = input("Podaj nowy klucz API Gemini: ").strip()
            if new_key:
                # Nadpisz w .env
                env_path = _get_env_path()
                env_content = ""
                if env_path.exists():
                    with open(env_path, 'r') as f:
                        env_content = f.read()
                    # Zamień stary klucz
                    import re
                    env_content = re.sub(
                        r'GEMINI_API_KEY=.*',
                        f'GEMINI_API_KEY={new_key}',
                        env_content
                    )
                else:
                    env_content = f"GEMINI_API_KEY={new_key}\n"

                with open(env_path, 'w') as f:
                    f.write(env_content)

                os.environ['GEMINI_API_KEY'] = new_key
                genai.configure(api_key=new_key)
                print("✅ Nowy klucz API zapisany.")
            else:
                print("❌ Nie podano klucza. Pomijam generowanie notatek.")
                return False
        else:
            return False

    # 4. Generowanie notatek
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')

        prompt = build_prompt(transcript_content, note_type, include_checklist)

        type_label = "ciągłe" if note_type == 'continuous' else "punktowane"
        checklist_label = " + checklista" if include_checklist else ""
        print(f"📝 Generowanie notatek ({type_label}{checklist_label})...")
        print("   To może potrwać chwilę...\n")

        response = model.generate_content(prompt)
        notes_content = response.text

        # Upewnij się, że folder docelowy istnieje
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(notes_content)

        print(f"✅ Notatki zapisane w: {output_path}")
        return True

    except Exception as e:
        print(f"❌ Błąd podczas generowania notatek: {e}")
        return False


# ─── Interactive Flow ──────────────────────────────────────────────────────────

def interactive_notes_flow(transcript_file_path: str, transcript_content: str) -> None:
    """
    Interaktywny flow — pytania po pobraniu transkrypcji.

    Args:
        transcript_file_path: Ścieżka do zapisanego pliku transkrypcji (np. Transcripts/Title.md)
        transcript_content: Sformatowana treść transkrypcji
    """
    print("\n" + "=" * 60)
    create_notes = input("📝 Czy utworzyć notatki z transkrypcji? (y/n): ").strip().lower()

    if create_notes != 'y':
        print("Pomijam generowanie notatek. Gotowe!")
        return

    # Typ notatki
    print("\nTyp notatki:")
    print("  (a) Ciągła   — spójny opis z podziałem na sekcje tematyczne")
    print("  (b) Punktowana — krótki opis sekcji + lista punktowana")
    note_choice = input("\nWybierz typ (a/b): ").strip().lower()

    if note_choice == 'a':
        note_type = 'continuous'
    elif note_choice == 'b':
        note_type = 'bullet'
    else:
        print("⚠️  Nieprawidłowy wybór, używam trybu punktowanego.")
        note_type = 'bullet'

    # Checklista
    checklist_choice = input("Dodać checklistę na końcu? (y/n): ").strip().lower()
    include_checklist = checklist_choice == 'y'

    # Ścieżka wyjściowa: Transcripts/Title.md → Transcripts/Title-notes.md
    base, ext = os.path.splitext(transcript_file_path)
    notes_output_path = f"{base}-notes{ext}"

    # Generuj notatki
    generate_notes(transcript_content, note_type, include_checklist, notes_output_path)
