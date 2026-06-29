from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

MOCK_INVOICES = {
    "INV-001": {"status": "paid", "payment_method": "Pix", "amount": "R$169.99"},
    "INV-002": {"status": "refund_pending", "payment_method": "credit card", "amount": "R$99.99"},
}


class InvoiceLookupInput(BaseModel):
    invoice_id: str = Field(..., description="The customer's invoice number to look up.")


class InvoiceLookupTool(BaseTool):
    name: str = "Invoice Lookup"
    description: str = (
        "Looks up the payment status, payment method, and amount for a specific invoice, "
        "given its invoice number."
    )
    args_schema: Type[BaseModel] = InvoiceLookupInput

    def _run(self, invoice_id: str) -> str:
        invoice = MOCK_INVOICES.get(invoice_id)
        if not invoice:
            return f"No invoice found with number {invoice_id}."
        return (
            f"Invoice {invoice_id}: status={invoice['status']}, "
            f"payment_method={invoice['payment_method']}, amount={invoice['amount']}"
        )