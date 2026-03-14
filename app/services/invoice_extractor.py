import base64
import json
from pathlib import Path
from typing import Any

from openai import OpenAI

from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.models.invoice_models import ExtractedInvoice
from app.services.tax_repository import TaxRepository


class InvoiceExtractor:
    MAX_ATTEMPTS = 2  # 1 retry

    def __init__(self, tax_repository: TaxRepository) -> None:
        if not OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is not configured. Please set it in your environment."
            )

        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.tax_repository = tax_repository
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        prompt_path = (
            Path(__file__).resolve().parent.parent
            / "prompts"
            / "invoice_extraction_prompt.txt"
        )
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

    def _build_response_schema(self) -> dict[str, Any]:
        allowed_categories = self.tax_repository.get_all_categories()

        return {
            "type": "json_schema",
            "name": "invoice_extraction",
            "strict": True,
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "invoice_id": {
                        "type": "string",
                        "description": "The invoice number or invoice identifier shown on the document.",
                    },
                    "special_notes": {
                        "type": ["string", "null"],
                        "description": "Invoice-level note related to tax handling or special instructions, or null if none.",
                    },
                    "apply_additional_tax": {
                        "type": "boolean",
                        "description": "False only if the invoice clearly indicates no additional tax should be added.",
                    },
                    "displayed_total": {
                        "type": ["number", "null"],
                        "description": "The final total shown on the invoice, or null if not clearly visible.",
                    },
                    "line_items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "description": {
                                    "type": "string",
                                    "description": "The line item description exactly as shown on the invoice.",
                                },
                                "quantity": {
                                    "type": "number",
                                    "description": (
                                        "The quantity for the line item. Use 1 if the row "
                                        "clearly represents a single billed item and quantity is omitted."
                                    ),
                                },
                                "unit_price": {
                                    "type": ["number", "null"],
                                    "description": "The per-unit price if clearly shown, otherwise null.",
                                },
                                "line_total": {
                                    "type": "number",
                                    "description": (
                                        "The total monetary amount for the row. Prefer the row total "
                                        "or extended amount over the unit price when both are shown."
                                    ),
                                },
                                "tax_category": {
                                    "type": "string",
                                    "enum": allowed_categories,
                                    "description": "Must be exactly one allowed tax category.",
                                },
                            },
                            "required": [
                                "description",
                                "quantity",
                                "unit_price",
                                "line_total",
                                "tax_category",
                            ],
                        },
                    },
                },
                "required": [
                    "invoice_id",
                    "special_notes",
                    "apply_additional_tax",
                    "displayed_total",
                    "line_items",
                ],
            },
        }

    def _parse_response_json(self, response: Any, file_name: str) -> dict[str, Any]:
        raw_output = response.output_text.strip()

        try:
            parsed_json = json.loads(raw_output)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"OpenAI structured output was not valid JSON for {file_name}. "
                f"Raw response: {raw_output}"
            ) from exc

        return parsed_json

    def _extract_once(self, file_bytes: bytes, file_name: str) -> ExtractedInvoice:
        prompt = self._build_prompt(file_name)
        encoded_pdf = base64.b64encode(file_bytes).decode("utf-8")
        response_schema = self._build_response_schema()

        response = self.client.responses.create(
            model=self.model,
            temperature=0,
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
            text={
                "format": response_schema,
            },
        )

        parsed_json = self._parse_response_json(response, file_name)

        prompt_tokens = 0
        completion_tokens = 0
        if getattr(response, "usage", None):
            prompt_tokens = getattr(response.usage, "input_tokens", 0) or 0
            completion_tokens = getattr(response.usage, "output_tokens", 0) or 0

        parsed_json["file_name"] = file_name
        parsed_json["ai_prompt_tokens"] = prompt_tokens
        parsed_json["ai_completion_tokens"] = completion_tokens

        return ExtractedInvoice(**parsed_json)

    def extract(self, file_bytes: bytes, file_name: str) -> ExtractedInvoice:
        last_error: Exception | None = None

        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            try:
                return self._extract_once(file_bytes, file_name)
            except ValueError as exc:
                last_error = exc
                if attempt == self.MAX_ATTEMPTS:
                    break

        raise ValueError(
            f"Failed to extract invoice data for {file_name} "
            f"after {self.MAX_ATTEMPTS} attempts. "
            f"Last error: {type(last_error).__name__}: {last_error}"
        ) from last_error