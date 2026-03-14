from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.pipeline import InvoiceProcessingPipeline
from app.services.document_loader import DocumentLoader
from app.services.invoice_extractor import InvoiceExtractor
from app.services.tax_engine import TaxEngine
from app.services.tax_repository import TaxRepository
from app.services.storage.local_json_writer import LocalJsonResultWriter
from app.config import INVOICE_OUTPUT_DIR, TAX_CSV_PATH

import traceback

router = APIRouter()


def get_pipeline() -> InvoiceProcessingPipeline:
    tax_repository = TaxRepository(TAX_CSV_PATH)
    document_loader = DocumentLoader()
    invoice_extractor = InvoiceExtractor(tax_repository=tax_repository)
    tax_engine = TaxEngine(tax_repository=tax_repository)
    result_writer = LocalJsonResultWriter(INVOICE_OUTPUT_DIR)

    return InvoiceProcessingPipeline(
        document_loader=document_loader,
        invoice_extractor=invoice_extractor,
        tax_engine=tax_engine,
        result_writer=result_writer,
    )


@router.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


from fastapi import APIRouter, UploadFile, File, HTTPException, status

router = APIRouter()

@router.post("/process-invoice", status_code=status.HTTP_200_OK)
async def process_invoice(file: UploadFile = File(...)) -> dict:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A file name is required.",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported.",
        )

    try:
        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        pipeline = get_pipeline()
        result = pipeline.process_uploaded_file(
            file_bytes=file_bytes,
            file_name=file.filename,
        )

        return result.model_dump()

    except HTTPException:
        raise
    except Exception as exc:
        print("==== FULL TRACEBACK ====")
        traceback.print_exc()
        print("========================")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process invoice: {type(exc).__name__}: {exc}",
        ) from exc