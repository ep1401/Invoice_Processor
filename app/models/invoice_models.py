from typing import List, Optional
from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str
    quantity: float = 1.0
    unit_price: Optional[float] = None
    line_total: float
    tax_category: str


class ExtractedInvoice(BaseModel):
    invoice_id: str
    file_name: str
    special_notes: Optional[str] = None
    apply_additional_tax: bool = True
    displayed_total: Optional[float] = None
    line_items: List[LineItem] = Field(default_factory=list)
    ai_prompt_tokens: int = 0
    ai_completion_tokens: int = 0