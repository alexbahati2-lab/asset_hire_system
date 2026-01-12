from django.shortcuts import render

# Create your views here.
# rentals/views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import json
from .models import Hire, Payment
from django.utils import timezone

@csrf_exempt
def c2b_callback(request):
    try:
        data = json.loads(request.body)
        trans_id = data.get('TransID')
        phone = data.get('MSISDN')
        amount = float(data.get('TransAmount', 0))
        bill_ref = data.get('BillRefNumber')  # maps to Hire.id

        hire = Hire.objects.filter(id=bill_ref).first()
        if hire:
            payment, created = Payment.objects.get_or_create(hire=hire)
            payment.amount = amount
            payment.status = "paid"
            payment.mpesa_receipt = trans_id
            payment.paid_at = timezone.now()
            payment.phone = phone
            payment.save()

            # Optionally update hire status too
            hire.status = "paid"
            hire.save()

        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
    except Exception as e:
        print("C2B Callback Error:", e)
        return JsonResponse({"ResultCode": 1, "ResultDesc": "Failed"})
