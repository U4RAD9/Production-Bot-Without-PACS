import requests
from django.conf import settings


def send_whatsapp_ticket(mobile_number, ticket_subject, overridebot="yes"):
    """
    Sends WhatsApp ticket assignment message using Cunnekt API
    mobile_number format: 91XXXXXXXXXX
    """

    if not settings.WHATSAPP_API_URL:
        return False, {"error": "WhatsApp API URL missing"}

    payload = {
        "templateid": settings.WHATSAPP_TEMPLATE_ID,
        "mobile": mobile_number,
        "overridebot": overridebot,
        "template": {
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": ticket_subject
                        }
                    ]
                }
            ]
        }
    }

    headers = {
        "Content-Type": "application/json",
        "API-KEY": settings.WHATSAPP_API_TOKEN   # ✅ MUST BE EXACT
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

        # Cunnekt success is based on JSON `status`, not HTTP 200
        return res_json.get("status", False), res_json

    except Exception as e:
        return False, {"error": str(e)}
