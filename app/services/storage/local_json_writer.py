import json
from pathlib import Path

from app.models.result_models import ProcessingResult
from app.services.storage.base import ResultWriter


class LocalJsonResultWriter(ResultWriter):
    def __init__(self, output_dir: str | Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_invoice_id(self, invoice_id: str) -> str:
        cleaned = "".join(
            char if char.isalnum() or char in {"-", "_"} else "_"
            for char in invoice_id
        ).strip("_")

        return cleaned or "unknown_invoice"

    def save(self, result: ProcessingResult) -> str:
        safe_invoice_id = self._sanitize_invoice_id(result.InvoiceID)
        output_path = self.output_dir / f"{safe_invoice_id}.json"

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(result.model_dump(), file, indent=2, ensure_ascii=False)

        return str(output_path)