import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
INVOICE_OUTPUT_DIR = OUTPUT_DIR / "invoices"
LOG_OUTPUT_DIR = OUTPUT_DIR / "logs"
SAMPLE_INVOICES_DIR = DATA_DIR / "sample_invoices"
TAX_CSV_PATH = DATA_DIR / "tax_rate_by_category.csv"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


def ensure_directories() -> None:
    INVOICE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)