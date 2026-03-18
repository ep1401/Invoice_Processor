from datetime import datetime, timezone

from app.models.invoice_models import ExtractedInvoice
from app.models.result_models import ProcessedLineItem, ProcessingResult
from app.services.tax_repository import TaxRepository


def round_money(value: float) -> float:
    return round(float(value), 2)


class TaxEngine:
    def __init__(self, tax_repository: TaxRepository) -> None:
        self.tax_repository = tax_repository

    def build_result(self, extracted_invoice: ExtractedInvoice) -> ProcessingResult:
        processed_line_items: list[ProcessedLineItem] = []

        invoice_pre_tax_total = 0.0
        invoice_tax_total = 0.0

        for item in extracted_invoice.line_items:
            line_total = round_money(item.line_total)
            tax_rate = self.tax_repository.get_tax_rate(item.tax_category)

            if extracted_invoice.apply_additional_tax:
                tax_amount = round_money(line_total * tax_rate)
            else:
                tax_amount = 0.0

            if item.unit_price is not None:
                unit_price = round_money(item.unit_price)
            elif item.quantity is not None and item.quantity != 0:
                unit_price = round_money(line_total / item.quantity)
            else:
                unit_price = None

            invoice_pre_tax_total += line_total
            invoice_tax_total += tax_amount

            processed_line_items.append(
                ProcessedLineItem(
                    Description=item.description,
                    Quantity=item.quantity,
                    UnitPrice=unit_price,
                    LineTotal=line_total,
                    TaxCategory=item.tax_category,
                    TaxAmount=tax_amount,
                )
            )

        invoice_pre_tax_total = round_money(invoice_pre_tax_total)
        invoice_tax_total = round_money(invoice_tax_total)
        invoice_post_tax_total = round_money(invoice_pre_tax_total + invoice_tax_total)

        return ProcessingResult(
            InvoiceID=extracted_invoice.invoice_id,
            FileName=extracted_invoice.file_name,
            AIPromptTokens=extracted_invoice.ai_prompt_tokens,
            AICompletionTokens=extracted_invoice.ai_completion_tokens,
            ProcessingDateTime=datetime.now(timezone.utc).isoformat(),
            InvoicePreTaxTotals=invoice_pre_tax_total,
            InvoiceTaxTotals=invoice_tax_total,
            InvoicePostTaxTotals=invoice_post_tax_total,
            InvoiceLineItems=processed_line_items,
            SpecialNotes=extracted_invoice.special_notes,
        )