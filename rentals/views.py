# rentals/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
import os
import requests
from requests.auth import HTTPBasicAuth

from .models import Hire, Payment

# -----------------------------
# M-PESA Access Token Helper
# -----------------------------
def get_mpesa_access_token():
    """
    Fetches an access token from Safaricom Daraja Sandbox.
    Uses environment variables if set; otherwise defaults to sandbox.
    """
    consumer_key = os.getenv("MPESA_CONSUMER_KEY", "D09FtPvxJeiXeeFzZVZvRnYzragBgyHlA3DDLQ5vGVlNAyHD")
    consumer_secret = os.getenv("MPESA_CONSUMER_SECRET", "qvmUSsX3HcMmRKBTc9Xgbq6g5apeqcMx6oec63GlkfS7ihnMP3ok5Z3dXSqCU25A")

    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    
    response = requests.get(url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    response.raise_for_status()  # Raise if HTTP error occurs

    data = response.json()
    token = data.get("access_token")
    if not token:
        raise Exception("Failed to retrieve M-Pesa access token.")
    return token

# -----------------------------
# Default Sandbox Paybill / Till
# -----------------------------
MPESA_PAYBILL = os.getenv("MPESA_PAYBILL", "600000")
MPESA_TILL = os.getenv("MPESA_TILL", "601234")

# -----------------------------
# C2B Callback Endpoint
# -----------------------------
@csrf_exempt
def c2b_callback(request):
    """
    M-Pesa C2B callback endpoint.

    Expected important fields from Safaricom:
        - TransID
        - TransAmount
        - MSISDN
        - BillRefNumber  -> maps to Hire.reference_id
    """
    if request.method != "POST":
        return JsonResponse({"ResultCode": 1, "ResultDesc": "Invalid request method"})

    try:
        # Parse JSON payload safely
        data = json.loads(request.body.decode("utf-8"))

        trans_id = data.get("TransID")
        phone = data.get("MSISDN")
        amount = float(data.get("TransAmount", 0))
        bill_ref = data.get("BillRefNumber")  # Maps to Hire.reference_id

        if not bill_ref:
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Missing BillRefNumber"})

        # Find the hire using reference_id
        hire = Hire.objects.filter(reference_id=bill_ref).first()
        if not hire:
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Hire not found"})

        # Prevent duplicate payments
        if Payment.objects.filter(mpesa_receipt=trans_id).exists():
            return JsonResponse({"ResultCode": 0, "ResultDesc": "Duplicate transaction ignored"})

        # Create the payment record
        payment = Payment.objects.create(
            hire=hire,
            amount=amount,
            phone=phone,
            mpesa_receipt=trans_id,
            status="success",
            paid_at=timezone.now(),
        )

        # Update hire status
        hire.status = "paid"
        hire.save()

        return JsonResponse({"ResultCode": 0, "ResultDesc": "Payment received successfully"})

    except json.JSONDecodeError:
        return JsonResponse({"ResultCode": 1, "ResultDesc": "Invalid JSON payload"})

    except Exception as e:
        print("❌ C2B CALLBACK ERROR:", str(e))
        return JsonResponse({"ResultCode": 1, "ResultDesc": "Internal server error"})
