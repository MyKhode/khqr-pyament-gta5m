import random
import string
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bakong_khqr import KHQR
from config import settings  # Updated import for config

# FastAPI app initialization
app = FastAPI()

# Request model only includes 'amount' (no 'bill_number' required anymore)
class PaymentRequest(BaseModel):
    amount: float

class PaymentStatusRequest(BaseModel):
    md5: str

# Function to generate a random bill number (using letters and digits)
def generate_random_bill_number(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# Function to get Bakong instance
def get_khqr_instance() -> KHQR:
    if not settings.BAKONG_DEV_TOKEN:
        raise HTTPException(status_code=500, detail="BAKONG_DEV_TOKEN is not configured")
    return KHQR(settings.BAKONG_DEV_TOKEN)

@app.post("/generate_qr")
def generate_khqr_payload(request: PaymentRequest):
    # Get the Bakong instance
    khqr = get_khqr_instance()

    # Always use "USD" as the currency
    curr = "USD"
    
    # Use the payee account from the .env file
    payee_account_id = settings.BAKONG_BANK_ACCOUNT

    # Generate a random bill number
    bill_number = generate_random_bill_number()

    try:
        # Generate the QR string for the payment
        qr_string = khqr.create_qr(
            bank_account=payee_account_id,
            merchant_name=settings.BAKONG_MERCHANT_NAME,
            merchant_city=settings.BAKONG_MERCHANT_CITY,
            amount=request.amount if curr != "KHR" else int(request.amount),
            currency=curr,
            store_label=settings.BAKONG_APP_NAME,
            phone_number=settings.BAKONG_PHONE_NUMBER,
            bill_number=bill_number,
            terminal_label="FastAPI-Server",
            static=False,
        )
        
        # Generate the deeplink with callback URL and app details
        deeplink = khqr.generate_deeplink(
            qr_string,
            callback=settings.BAKONG_CALLBACK_URL,
            appIconUrl=settings.BAKONG_APP_ICON_URL,
            appName=settings.BAKONG_APP_NAME,
        )

        # Generate MD5 for the QR code
        md5 = khqr.generate_md5(qr_string)

        # Return the QR code payload
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
