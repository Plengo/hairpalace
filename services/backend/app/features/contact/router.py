from fastapi import APIRouter

from app.features.contact.schemas import ContactFormIn
from app.features.contact.service import ContactService

router = APIRouter(prefix="/contact", tags=["Contact"])


@router.post("", status_code=202)
async def contact_form(payload: ContactFormIn) -> dict:
    svc = ContactService()
    await svc.submit(payload)
    return {"detail": "Message received. We'll be in touch within 1–2 business days."}
