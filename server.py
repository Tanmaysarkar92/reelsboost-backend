from fastapi import FastAPI, Request, Header
import hmac, hashlib, json, os
from supabase import create_client

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def verify_signature(body, signature):
    generated = hmac.new(
        bytes(WEBHOOK_SECRET, 'utf-8'),
        body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(generated, signature)

@app.get("/")
def home():
    return {"status": "Backend running"}

@app.post("/webhook")
async def webhook(request: Request, x_razorpay_signature: str = Header(None)):
    body = await request.body()

    if not verify_signature(body, x_razorpay_signature):
        return {"error": "Invalid signature"}

    data = json.loads(body)

    if data["event"] == "payment.captured":
        email = data["payload"]["payment"]["entity"]["notes"]["email"]

        supabase.table("users").upsert({
            "email": email,
            "is_pro": True
        }).execute()

    return {"status": "ok"}