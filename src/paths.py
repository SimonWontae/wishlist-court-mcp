from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"

WISHLIST_CSV = DATA_DIR / "wishlist.csv"
OWNED_ITEMS_CSV = DATA_DIR / "owned_items.csv"
BUDGET_JSON = DATA_DIR / "budget.json"
