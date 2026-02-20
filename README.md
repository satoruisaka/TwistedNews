# TwistedNews

**TwistedNews** is an automated news commentary generator that processes news articles from NewsAgent, groups them by original language, and generates insightful commentary using intelligent prompt engineering.

## How it works

TwistedNews reads news article markdown files from data directory, detects the original language from filenames, groups articles by language and date, then uses the TwistedPair REST API with TwistedPair's rhetorical distortion modes to generate sophisticated, context-rich commentary on the day's news for each language group, and sends the result via email.

## Architecture

```
┌─────────────────────┐
│  News Articles Dir  │
│  (MRA/markdown/)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Language Detector  │
│  (from filename)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Group by Language  │
│  (per date)         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Prompt Builder     │
│  (comprehensive/    │
│   simple/raw)       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  TwistedPair API    │
│  (mode + tone +     │
│   gain + prompt)    │
└──────────┬──────────┘
           │
           ├──────────────┐
           ▼              ▼
┌──────────────┐  ┌──────────────┐
│ Save to MD   │  │ Email Report │
│ (twistednews)│  │ (Full Text)  │
└──────────────┘  └──────────────┘
```

### Project Structure

```
TwistedNews/
├── config.py              # Configuration and environment variables
├── models.py              # Data structures (NewsArticle, LanguageGroup, etc.)
├── prompts.py             # Prompt templates for LLM commentary generation
├── language_detector.py   # Language detection from filenames
├── twistedpair_client.py  # TwistedPair REST API client
├── email_delivery.py      # Email notification with HTML formatting
├── main.py                # Main processing pipeline
├── run_twistednews.sh     # Startup script with venv auto-activation
├── requirements.txt       # Python dependencies
├── .env.example           # Environment configuration template
├── .env                   # Your environment configuration (create this)
├── README.md              # This file
├── LICENSE                # MIT license file
└── .venv/                 # Virtual environment (create with python3 -m venv .venv)

Project Root:
└── startTwistedNews.sh    # Cron wrapper script (in /home/sator/project/)
```

## Installation

### 1. Prerequisites

- Python 3.10+
- **TwistedPair V2** server running on `localhost:8001`
- **Ollama** with suitable models installed
- SMTP email account for notifications

### 2. Set Up Virtual Environment (Recommended)

```bash
cd TwistedNews
python3 -m venv .venv
source ./.venv/bin/activate
pip install -r requirements.txt
```

> **Note:** The startup script automatically activates `.venv` or `venv` if it exists.

### 3. Configuration

Create a `.env` file in the TwistedNews directory:

## Usage

### Quick Start

Use the startup script (automatically activates virtual environment):
```bash
./run_twistednews.sh
```

Or run directly:
```bash
python main.py
```

### Process Specific Date

```bash
python main.py --date 20260219
```

### Skip Email Notification

```bash
python main.py --no-email
```

### Custom Articles Directory

```bash
python main.py --articles-dir /path/to/articles
```

### Help

```bash
python main.py --help
```

## Input Format

TwistedNews expects markdown files in the following format:

**Filename:** `YYYYMMDD_HHMMSS_title_in_original_language.md`

Examples:
- `20260219_053045_Quién_es_el_ex_príncipe_Andrés.md` (Spanish)
- `20260219_052602_بريطانيا_تمنع_صينياً_مقرباً_من.md` (Arabic)
- `20260121_050226_我国科学家巧打"中国结"给磁场拍出高清照.md` (Chinese)

The language is detected automatically from the characters in the title.

## Output Format

Generated commentary files are saved to `/MRA/data/markdown/twistednews/`:

**Filename:** `YYYYMMDD_XX.md` where XX is the language code (CN, RU, HE, AR, SP)

## Language Detection

Languages are detected from filename title using Unicode character ranges:

| Language | Character Range | Code |
|----------|----------------|------|
| Chinese  | CJK Unified Ideographs (U+4E00–U+9FFF) | CN |
| Russian  | Cyrillic (U+0400–U+04FF) | RU |
| Hebrew   | Hebrew (U+0590–U+05FF) | HE |
| Arabic   | Arabic (U+0600–U+06FF) | AR |
| Spanish  | Latin + accents (áéíóúñ) | SP |

## Prompt Styles

TwistedNews uses intelligent prompt templates to guide the LLM in generating useful commentary:

### `comprehensive` (Default)
Detailed analytical commentary with:
- Key themes identification across all articles
- Cross-article connections and patterns
- Historical, political, and cultural context
- Implications analysis
- Divergent perspectives
- 500-800 word synthesis

### `simple`
Basic summarization:
- Main topic per article (1 sentence)
- Key points (2-3 bullets)
- Significance (1 sentence)
- Overall synthesis

### `raw`
No prompt wrapper (original behavior):
- Sends raw concatenated articles to TwistedPair
- Relies entirely on distortion mode

Configure via `.env`:
```bash
PROMPT_STYLE=comprehensive  # or simple, or raw
```

## TwistedPair Modes

Choose the rhetorical mode for commentary generation:

- **`so_what_er`** - "So what?" analysis (default for news)
- **`cucumb_er`** - Evidence-based critique
- **`invert_er`** - Contrarian perspective
- **`echo_er`** - Affirmation and expansion
- **`what_if_er`** - Speculative scenarios
- **`archiv_er`** - Historical contextualization

## Integration with MRA

TwistedNews is designed to work seamlessly with the MRA system:

- **Input:** Reads from `MRA/data/markdown/news_articles/`
- **Output:** Writes to `MRA/data/markdown/twistednews/`
- **Format:** Uses same markdown format as MRA
- **Indexing:** Output files can be indexed by MRA's FAISS system

## Email Notification

After processing, a rich HTML email is sent containing:

- **Summary Statistics** - Languages processed, article count, commentaries generated
- **Full Commentary Content** - Complete generated text for each language group
- **Metadata** - TwistedPair parameters (mode, tone, gain), timestamps
- **File References** - Output file paths for archival

The email includes both HTML (with styling and formatting) and plain text versions for maximum compatibility.



## License

MIT License

## Support

Sorry, no support available.

## Created and last modified

February 19, 2026 by Satoru Isaka
