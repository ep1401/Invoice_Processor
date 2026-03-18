import csv
from pathlib import Path

import pytest

from app.models.invoice_models import ExtractedInvoice, LineItem
from app.models.result_models import ProcessedLineItem, ProcessingResult


@pytest.fixture
def tax_csv_path(tmp_path: Path) -> Path:
    csv_path = tmp_path / "tax_rate_by_category.csv"

    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Category", "Tax Rate (%)"])
        writer.writerow(["Fresh Produce", "0"])
        writer.writerow(["Prepared Food", "8.25"])
        writer.writerow(["Office Supplies", "6.50"])

    return csv_path


@pytest.fixture
def extracted_invoice_taxable() -> ExtractedInvoice:
    return ExtractedInvoice(
        invoice_id="INV-1001",
        file_name="Invoice 1.pdf",
        displayed_total=18.41,
        apply_additional_tax=True,
        special_notes=None,
        ai_prompt_tokens=100,
        ai_completion_tokens=25,
        line_items=[
            LineItem(
                description="Notebook",
                quantity=2,
                unit_price=5.00,
                line_total=10.00,
                tax_category="Office Supplies",
            ),
            LineItem(
                description="Sandwich",
                quantity=1,
                unit_price=7.90,
                line_total=7.90,
                tax_category="Prepared Food",
            ),
        ],
    )


@pytest.fixture
def extracted_invoice_non_taxable() -> ExtractedInvoice:
    return ExtractedInvoice(
        invoice_id="INV-2002",
        file_name="Invoice 2.pdf",
        displayed_total=11.50,
        apply_additional_tax=False,
        special_notes="Tax already included on invoice.",
        ai_prompt_tokens=120,
        ai_completion_tokens=30,
        line_items=[
            LineItem(
                description="Apples",
                quantity=5,
                unit_price=2.30,
                line_total=11.50,
                tax_category="Fresh Produce",
            ),
        ],
    )


@pytest.fixture
def sample_processing_result() -> ProcessingResult:
    return ProcessingResult(
        InvoiceID="INV-1001",
        FileName="Invoice 1.pdf",
        AIPromptTokens=100,
        AICompletionTokens=25,
        ProcessingDateTime="2026-03-14T12:00:00+00:00",
        InvoicePreTaxTotals=17.90,
        InvoicePostTaxTotals=19.06,
        InvoiceTaxTotals=1.16,
        InvoiceLineItems=[
            ProcessedLineItem(
                Description="Notebook",
                Quantity=2,
                UnitPrice=5.00,
                LineTotal=10.00,
                TaxCategory="Office Supplies",
                TaxAmount=0.65,
            ),
            ProcessedLineItem(
                Description="Sandwich",
                Quantity=1,
                UnitPrice=7.90,
                LineTotal=7.90,
                TaxCategory="Prepared Food",
                TaxAmount=0.51,
            ),
        ],
        SpecialNotes=None,
    )