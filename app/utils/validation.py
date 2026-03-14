from typing import List

from app.models.invoice_models import ExtractedInvoice


def round_money(value: float) -> float:
    return round(float(value), 2)


def validate_extracted_invoice(extracted_invoice: ExtractedInvoice) -> List[str]:
    warnings: List[str] = []

    if not extracted_invoice.invoice_id:
        raise ValueError("Missing invoice_id.")

    if not extracted_invoice.file_name:
        raise ValueError("Missing file_name.")

    if not extracted_invoice.line_items:
        raise ValueError("No line items were extracted.")

    computed_pre_tax_total = 0.0

    for index, item in enumerate(extracted_invoice.line_items, start=1):
        if not item.description:
            raise ValueError(f"Line item {index} is missing description.")

        if item.line_total is None:
            raise ValueError(f"Line item {index} is missing line_total.")

        if not item.tax_category:
            raise ValueError(f"Line item {index} is missing tax_category.")

        computed_pre_tax_total += float(item.line_total)

        # quantity * unit_price ~= line_total
        if item.unit_price is not None:
            expected_line_total = round_money(float(item.quantity) * float(item.unit_price))
            actual_line_total = round_money(float(item.line_total))

            if abs(expected_line_total - actual_line_total) > 0.01:
                warnings.append(
                    f"Line item {index} total mismatch: "
                    f"quantity * unit_price = {expected_line_total}, "
                    f"but line_total = {actual_line_total}."
                )

    computed_pre_tax_total = round_money(computed_pre_tax_total)

    # sum(line totals) ~= displayed total
    if extracted_invoice.displayed_total is not None:
        displayed_total = round_money(float(extracted_invoice.displayed_total))

        if abs(computed_pre_tax_total - displayed_total) > 0.01:
            warnings.append(
                f"Invoice total mismatch: summed line totals = {computed_pre_tax_total}, "
                f"but displayed_total = {displayed_total}."
            )

    return warnings