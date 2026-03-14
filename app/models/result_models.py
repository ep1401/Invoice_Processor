from typing import List, Optional
from pydantic import BaseModel


class ProcessedLineItem(BaseModel):
    Description: str
    Quantity: float = 1.0
    UnitPrice: Optional[float] = None
    LineTotal: float
    TaxCategory: str
    TaxAmount: float


class ProcessingResult(BaseModel):
    InvoiceID: str
    FileName: str
    AIPromptTokens: int
    AICompletionTokens: int
    ProcessingDateTime: str
    InvoicePreTaxTotals: float
    InvoicePostTaxTotals: float
    InvoiceTaxTotals: float
    InvoiceLineItems: List[ProcessedLineItem]
    SpecialNotes: Optional[str] = None