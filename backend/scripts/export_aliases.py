
import json
import sys
from pathlib import Path

# Add the backend root directory to Python's import path.
BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

from app.services.indian_name_service import ALIASES

output_path = BACKEND_ROOT / "app" / "data" / "indian_ingredient_aliases.json"
output_path.parent.mkdir(parents=True, exist_ok=True)

records = [
    {
        "alias": alias,
        "canonical_name": canonical_name,
        "language": language,
        "source": "manually_curated_prototype",
        "review_status": "needs_source_review",
    }
    for alias, (canonical_name, language) in sorted(ALIASES.items())
]

output_path.write_text(
    json.dumps(records, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

print(f"Exported {len(records)} aliases to {output_path}")
