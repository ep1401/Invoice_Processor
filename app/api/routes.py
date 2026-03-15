from fastapi import APIRouter, File, HTTPException, UploadFile, status
import traceback

from app.config import OUTPUT_DIR, TAX_CSV_PATH
from app.pipeline import InvoiceProcessingPipeline
from app.services.document_validator import DocumentValidator
from app.services.invoice_extractor import InvoiceExtractor
from app.services.storage.local_json_writer import LocalJsonResultWriter
from app.services.tax_engine import TaxEngine
from app.services.tax_repository import TaxRepository

router = APIRouter()


def get_pipeline() -> InvoiceProcessingPipeline:
    tax_repository = TaxRepository(TAX_CSV_PATH)
    document_validator = DocumentValidator()
    invoice_extractor = InvoiceExtractor(tax_repository=tax_repository)
    tax_engine = TaxEngine(tax_repository=tax_repository)
    result_writer = LocalJsonResultWriter(OUTPUT_DIR)

    return InvoiceProcessingPipeline(
        document_validator=document_validator,
        invoice_extractor=invoice_extractor,
        tax_engine=tax_engine,
        result_writer=result_writer,
    )


@router.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@router.post("/process-invoice", status_code=status.HTTP_200_OK)
async def process_invoice(file: UploadFile = File(...)) -> dict:
    try:
        file_bytes = await file.read()

        pipeline = get_pipeline()
        result = pipeline.process_uploaded_file(
            file_bytes=file_bytes,
            file_name=file.filename or "",
        )

        return result.model_dump()

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print("==== FULL TRACEBACK ====")
        traceback.print_exc()
        print("========================")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process invoice: {type(exc).__name__}: {exc}",
        ) from exc