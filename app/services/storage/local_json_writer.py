import json
from pathlib import Path

from app.models.result_models import ProcessingResult
from app.services.storage.base import ResultWriter


class LocalJsonResultWriter(ResultWriter):
    def __init__(self, output_dir: str | Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_component(self, value: str | None, fallback: str) -> str:
        if not value:
            return fallback

        cleaned = "".join(
            char if char.isalnum() or char in {"-", "_"} else "_"
            for char in value
        ).strip("_")

        return cleaned or fallback

    def save(self, result: ProcessingResult) -> str:
        safe_invoice_id = self._sanitize_component(result.InvoiceID, "UNKNOWN_INVOICE_ID")
        pdf_stem = Path(result.FileName).stem
        safe_pdf_stem = self._sanitize_component(pdf_stem, "unknown_file")

        output_path = self.output_dir / f"{safe_invoice_id}__{safe_pdf_stem}.json"

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(result.model_dump(), file, indent=2, ensure_ascii=False)

        return str(output_path)