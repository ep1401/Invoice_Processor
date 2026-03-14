import csv
from pathlib import Path


class TaxRepository:
    def __init__(self, csv_path: str | Path) -> None:
        self.csv_path = Path(csv_path)
        self._tax_rates = self._load_tax_rates()

    def _load_tax_rates(self) -> dict[str, float]:
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Tax CSV not found: {self.csv_path}")

        last_error: Exception | None = None

        for encoding in ("utf-8-sig", "cp1252", "latin-1"):
            try:
                tax_rates: dict[str, float] = {}

                with open(self.csv_path, "r", encoding=encoding, newline="") as file:
                    reader = csv.DictReader(file)

                    for row in reader:
                        category = str(row["Category"]).strip()
                        tax_rate_percent = float(row["Tax Rate (%)"])
                        tax_rates[category] = tax_rate_percent / 100.0

                if not tax_rates:
                    raise ValueError("No tax categories were loaded from the CSV.")

                return tax_rates

            except UnicodeDecodeError as exc:
                last_error = exc
                continue

        raise ValueError(f"Could not read tax CSV with supported encodings. Last error: {last_error}")

    def get_tax_rate(self, category: str) -> float:
        category = category.strip()

        if category not in self._tax_rates:
            raise ValueError(f"Unknown tax category: {category}")

        return self._tax_rates[category]

    def get_all_categories(self) -> list[str]:
        return list(self._tax_rates.keys())