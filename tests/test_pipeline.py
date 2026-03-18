import json
from pathlib import Path

from app.pipeline import InvoiceProcessingPipeline
from app.services.storage.local_json_writer import LocalJsonResultWriter
from app.services.tax_engine import TaxEngine
from app.services.tax_repository import TaxRepository


class FakeInputDocument:
    def __init__(self, file_bytes: bytes, file_name: str):
        self.file_bytes = file_bytes
        self.file_name = file_name


class FakeDocumentValidator:
    def validate(self, file_bytes: bytes, file_name: str):
        return FakeInputDocument(file_bytes=file_bytes, file_name=file_name)


class FakeInvoiceExtractor:
    def __init__(self, extracted_invoice):
        self.extracted_invoice = extracted_invoice

    def extract(self, file_bytes: bytes, file_name: str):
        return self.extracted_invoice


def test_pipeline_processes_invoice_end_to_end_with_mocked_extractor(
    tmp_path: Path,
    tax_csv_path,
    extracted_invoice_taxable,
):
    tax_repository = TaxRepository(tax_csv_path)
    tax_engine = TaxEngine(tax_repository=tax_repository)
    result_writer = LocalJsonResultWriter(tmp_path)

    pipeline = InvoiceProcessingPipeline(
        document_validator=FakeDocumentValidator(),
        invoice_extractor=FakeInvoiceExtractor(extracted_invoice_taxable),
        tax_engine=tax_engine,
        result_writer=result_writer,
    )

    result = pipeline.process_uploaded_file(
        file_bytes=b"%PDF-1.4 fake pdf bytes",
        file_name="Invoice 1.pdf",
    )

    assert result.InvoiceID == "INV-1001"
    assert result.FileName == "Invoice 1.pdf"
    assert abs(result.InvoicePreTaxTotals - 17.90) < 0.01
    assert abs(result.InvoiceTaxTotals - 1.30) < 0.01
    assert abs(result.InvoicePostTaxTotals - 19.20) < 0.01
    assert len(result.InvoiceLineItems) == 2

    saved_path = tmp_path / "INV-1001__Invoice_1.json"
    assert saved_path.exists()

    with open(saved_path, "r", encoding="utf-8") as file:
        saved = json.load(file)

    assert saved["InvoiceID"] == "INV-1001"
    assert saved["FileName"] == "Invoice 1.pdf"
    assert len(saved["InvoiceLineItems"]) == 2