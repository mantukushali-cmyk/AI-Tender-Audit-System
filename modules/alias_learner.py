import json
import os

ALIAS_FILE = "modules/alias_store.json"


def load_alias_store():
    if not os.path.exists(ALIAS_FILE):
        return {}
    try:
        with open(ALIAS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except json.JSONDecodeError:
        return {}


def save_alias_store(data):
    with open(ALIAS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def learn_alias(
    raw_name=None,
    canonical_name=None,
    *,
    raw_alias=None,
    assigned_standard=None,
    requires_manual_review=False,
):
    raw_name = raw_name or raw_alias
    canonical_name = canonical_name or assigned_standard

    if not raw_name or not canonical_name:
        raise ValueError("raw_name and canonical_name are required")

    store = load_alias_store()
    key = canonical_name.lower()

    if key not in store:
        store[key] = []

    entry = {
        "raw_name": raw_name,
        "requires_manual_review": requires_manual_review,
    }

    if entry not in store[key]:
        store[key].append(entry)

    save_alias_store(store)
def find_learned_match(raw_name: str, threshold=0.75):
    """
    Try to match unknown document to learned structured aliases
    """
    store = load_alias_store()

    best_match = None
    best_score = 0

    for canonical, entries in store.items():
        # Handle backward-compatibility: if the store has old string arrays or new dict arrays
        for entry in entries:
            # 1. Safely extract the target string to compare against
            if isinstance(entry, dict):
                alias_str = entry.get("raw_name", "")
            else:
                alias_str = entry  # Fallback for old simple-string JSON entries

            # 2. Run your existing similarity computation
            score = similarity(raw_name.lower(), alias_str.lower())

            if score > best_score:
                best_score = score
                best_match = canonical

    if best_score >= threshold:
        return best_match

    return None


def similarity(a, b):
    from difflib import SequenceMatcher
    return SequenceMatcher(None, a, b).ratio()