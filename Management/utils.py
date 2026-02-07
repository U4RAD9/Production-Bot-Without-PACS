import requests
from django.conf import settings

def send_whatsapp_ticket(mobile_number, overridebot="yes"):
    """
    Sends WhatsApp ticket assignment message using Cunnekt API
    mobile_number format: 91XXXXXXXXXX
    Template is STATIC (no variables)
    """

    if not settings.WHATSAPP_API_URL:
        return False, {"error": "WhatsApp API URL missing"}

    payload = {
        "templateid": settings.WHATSAPP_TEMPLATE_ID,
        "mobile": mobile_number,
        "overridebot": overridebot
        # ❌ No template/components because template has no variables
    }

    headers = {
        "Content-Type": "application/json",
        "API-KEY": settings.WHATSAPP_API_TOKEN   # ✅ Must be exact
    }

    try:
        response = requests.post(
            settings.WHATSAPP_API_URL,
            headers=headers,
            json=payload,
            timeout=10
        )

        print("📡 WhatsApp API Status:", response.status_code)
        print("📡 WhatsApp API Response:", response.text)

        res_json = response.json()

        # Success is determined by JSON "status", not HTTP 200
        return res_json.get("status", False), res_json

    except Exception as e:
        return False, {"error": str(e)}
