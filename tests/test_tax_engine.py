from app.services.tax_engine import TaxEngine
from app.services.tax_repository import TaxRepository


def test_tax_engine_computes_totals_correctly(tax_csv_path, extracted_invoice_taxable):
    repo = TaxRepository(tax_csv_path)
    engine = TaxEngine(tax_repository=repo)

    result = engine.build_result(extracted_invoice_taxable)

    assert result.InvoiceID == "INV-1001"
    assert result.FileName == "Invoice 1.pdf"
    assert result.AIPromptTokens == 100
    assert result.AICompletionTokens == 25

    assert abs(result.InvoicePreTaxTotals - 17.90) < 0.01
    assert abs(result.InvoiceTaxTotals - 1.30) < 0.01
    assert abs(result.InvoicePostTaxTotals - 19.20) < 0.01

    assert len(result.InvoiceLineItems) == 2
    assert result.InvoiceLineItems[0].TaxCategory == "Office Supplies"
    assert abs(result.InvoiceLineItems[0].TaxAmount - 0.65) < 0.01
    assert result.InvoiceLineItems[1].TaxCategory == "Prepared Food"
    assert abs(result.InvoiceLineItems[1].TaxAmount - 0.65) < 0.01


def test_tax_engine_skips_additional_tax_when_flag_is_false(
    tax_csv_path, extracted_invoice_non_taxable
):
    repo = TaxRepository(tax_csv_path)
    engine = TaxEngine(tax_repository=repo)

    result = engine.build_result(extracted_invoice_non_taxable)

    assert abs(result.InvoicePreTaxTotals - 11.50) < 0.01
    assert abs(result.InvoiceTaxTotals - 0.00) < 0.01
    assert abs(result.InvoicePostTaxTotals - 11.50) < 0.01

    assert len(result.InvoiceLineItems) == 1
    assert abs(result.InvoiceLineItems[0].TaxAmount - 0.00) < 0.01