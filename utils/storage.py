import json
import os
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DRAFTS_FILE = DATA_DIR / "drafts.json"


def _ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)


def load_drafts() -> list[dict]:
    _ensure_data_dir()
    if not DRAFTS_FILE.exists():
        return []
    with open(DRAFTS_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_draft(title: str, content: str, category: str, scheduled_at: str | None = None) -> dict:
    drafts = load_drafts()
    draft = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "title": title,
        "content": content,
        "category": category,
        "created_at": datetime.now().isoformat(),
        "scheduled_at": scheduled_at,
    }
    drafts.append(draft)
    _ensure_data_dir()
    with open(DRAFTS_FILE, "w", encoding="utf-8") as f:
        json.dump(drafts, f, ensure_ascii=False, indent=2)
    return draft


def delete_draft(draft_id: str) -> bool:
    drafts = load_drafts()
    new_drafts = [d for d in drafts if d["id"] != draft_id]
    if len(new_drafts) == len(drafts):
        return False
    with open(DRAFTS_FILE, "w", encoding="utf-8") as f:
        json.dump(new_drafts, f, ensure_ascii=False, indent=2)
    return True


def update_draft(draft_id: str, title: str, content: str) -> bool:
    drafts = load_drafts()
    for d in drafts:
        if d["id"] == draft_id:
            d["title"] = title
            d["content"] = content
            d["updated_at"] = datetime.now().isoformat()
            with open(DRAFTS_FILE, "w", encoding="utf-8") as f:
                json.dump(drafts, f, ensure_ascii=False, indent=2)
            return True
    return False
