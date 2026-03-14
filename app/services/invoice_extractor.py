import base64
import json
from pathlib import Path

from openai import OpenAI

from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.models.invoice_models import ExtractedInvoice
from app.services.tax_repository import TaxRepository


class InvoiceExtractor:
    def __init__(self, tax_repository: TaxRepository) -> None:
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.tax_repository = tax_repository
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "invoice_extraction_prompt.txt"
        return prompt_path.read_text(encoding="utf-8")

    def _build_prompt(self, file_name: str) -> str:
        allowed_categories = "\n".join(
            f"- {category}" for category in self.tax_repository.get_all_categories()
        )
        return (
            self.prompt_template
            .replace("{allowed_categories}", allowed_categories)
            .replace("{file_name}", file_name)
        )

    def extract(self, file_bytes: bytes, file_name: str) -> ExtractedInvoice:
        prompt = self._build_prompt(file_name)
        encoded_pdf = base64.b64encode(file_bytes).decode("utf-8")

        response = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt,
                        },
                        {
                            "type": "input_file",
                            "filename": file_name,
                            "file_data": f"data:application/pdf;base64,{encoded_pdf}",
                        },
                    ],
                }
            ],
        )

        raw_output = response.output_text.strip()

        try:
            parsed_json = json.loads(raw_output)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"OpenAI response was not valid JSON. Raw response: {raw_output}"
            ) from exc

        prompt_tokens = 0
        completion_tokens = 0

        if getattr(response, "usage", None):
            prompt_tokens = getattr(response.usage, "input_tokens", 0) or 0
            completion_tokens = getattr(response.usage, "output_tokens", 0) or 0

        parsed_json["file_name"] = file_name
        parsed_json["ai_prompt_tokens"] = prompt_tokens
        parsed_json["ai_completion_tokens"] = completion_tokens

        return ExtractedInvoice(**parsed_json)