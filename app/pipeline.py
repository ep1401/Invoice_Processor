from app.models.invoice_models import ExtractedInvoice
from app.models.result_models import ProcessingResult
from app.services.document_loader import DocumentLoader
from app.services.invoice_extractor import InvoiceExtractor
from app.services.tax_engine import TaxEngine
from app.services.storage.base import ResultWriter
from app.utils.validation import validate_extracted_invoice


class InvoiceProcessingPipeline:
    def __init__(
        self,
        document_loader: DocumentLoader,
        invoice_extractor: InvoiceExtractor,
        tax_engine: TaxEngine,
        result_writer: ResultWriter,
    ) -> None:
        self.document_loader = document_loader
        self.invoice_extractor = invoice_extractor
        self.tax_engine = tax_engine
        self.result_writer = result_writer

    def process_uploaded_file(self, file_bytes: bytes, file_name: str) -> ProcessingResult:
        loaded_document = self.document_loader.load_from_bytes(
            file_bytes=file_bytes,
            file_name=file_name,
        )

        extracted_invoice: ExtractedInvoice = self.invoice_extractor.extract(
            file_bytes=loaded_document.file_bytes,
            file_name=loaded_document.file_name,
        )

        warnings = validate_extracted_invoice(extracted_invoice)

        result: ProcessingResult = self.tax_engine.build_result(extracted_invoice)

        if warnings:
            warning_text = " | ".join(warnings)
            if result.SpecialNotes:
                result.SpecialNotes = f"{result.SpecialNotes} | Validation warnings: {warning_text}"
            else:
                result.SpecialNotes = f"Validation warnings: {warning_text}"

        self.result_writer.save(result)

        return result