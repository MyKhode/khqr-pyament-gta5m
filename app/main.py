from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bakong_khqr import KHQR
from typing import Optional
from config import settings


# FastAPI app initialization
app = FastAPI()


# Request models
class PaymentRequest(BaseModel):
    payee_account_id: str
    amount: float
    currency: Optional[str] = "USD"
    bill_number: str


class PaymentStatusRequest(BaseModel):
    md5: str


# Function to get Bakong instance
def get_khqr_instance() -> KHQR:
    if not settings.BAKONG_DEV_TOKEN:
        raise HTTPException(status_code=500, detail="BAKONG_DEV_TOKEN is not configured")
    return KHQR(settings.BAKONG_DEV_TOKEN)


# Generate QR code payload
@app.post("/generate_qr")
def generate_khqr_payload(request: PaymentRequest):
    khqr = get_khqr_instance()
    curr = (request.currency or settings.BAKONG_DEFAULT_CURRENCY).upper()
    phone = settings.BAKONG_PHONE_NUMBER or "85500000000"

    try:
        qr_string = khqr.create_qr(
            bank_account=request.payee_account_id,
            merchant_name=settings.BAKONG_MERCHANT_NAME,
            merchant_city=settings.BAKONG_MERCHANT_CITY,
            amount=request.amount if curr != "KHR" else int(request.amount),
            currency=curr,
            store_label=settings.BAKONG_APP_NAME,
            phone_number=phone,
            bill_number=request.bill_number,
            terminal_label="FastAPI-Server",
            static=False,
        )
        deeplink = khqr.generate_deeplink(
            qr_string,
            callback=settings.BAKONG_CALLBACK_URL,
            appIconUrl=settings.BAKONG_APP_ICON_URL,
            appName=settings.BAKONG_APP_NAME,
        )

        md5 = khqr.generate_md5(qr_string)

        return {"qr_string": qr_string, "deeplink": deeplink, "md5": md5}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating QR: {str(e)}")


# Check payment status
@app.post("/check_payment_status")
def check_payment_status(request: PaymentStatusRequest):
    khqr = get_khqr_instance()

    try:
        status = khqr.check_payment(request.md5)
        return {"payment_status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking payment status: {str(e)}")
