# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py

# Run on a specific port
streamlit run app.py --server.port 8502
```

## Architecture

This is a personal AI writing assistant built with Streamlit + Gemini API. No database or authentication.

### Data flow

Every page follows the same pattern:
1. User fills in form inputs (topic, tone, length, etc.)
2. Page builds a Japanese prompt string from those inputs
3. `utils/gemini_client.py:stream_generate()` streams the response chunk-by-chunk into a `st.empty()` placeholder
4. User can save the result via `utils/storage.py:save_draft()` → persisted to `data/drafts.json`

### Key modules

- **`utils/gemini_client.py`** — thin wrapper around `google-generativeai`. Default model is `gemini-2.0-flash`. `stream_generate()` is used by all pages; `generate()` (non-streaming) exists but is currently unused.
- **`utils/storage.py`** — flat-file JSON persistence at `data/drafts.json`. Draft IDs are timestamp strings (`%Y%m%d%H%M%S%f`). The scheduler page (`pages/3_scheduler.py`) is the only place drafts are read and managed; all other pages only write via `save_draft()`.

### Adding a new page

Pages live in `pages/` and are auto-discovered by Streamlit in filename-alphabetical order. Each page must:
- Call `sys.path.append(str(Path(__file__).parent.parent))` before importing from `utils/`
- Call `st.set_page_config(...)` as the first Streamlit call

### Environment

Requires a `.env` file at the project root with `GEMINI_API_KEY`. The key is loaded once at import time via `python-dotenv` in `gemini_client.py`. If the key is missing, `get_model()` raises `ValueError` immediately on first generation attempt.
