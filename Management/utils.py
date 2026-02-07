import requests
from django.conf import settings


def send_whatsapp_ticket(mobile_number, overridebot="yes"):
    """
    Sends WhatsApp message using Cunnekt API
    mobile_number format: 91XXXXXXXXXX
    """

    if not settings.WHATSAPP_API_URL:
        return False, "WhatsApp API URL missing"

    payload = {
        "mobile": mobile_number,
        "templateid": settings.WHATSAPP_TEMPLATE_ID,
        "overridebot": overridebot
    }

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            settings.WHATSAPP_API_URL,
            json=payload,
            headers=headers,
            timeout=10
        )

        print("📡 WhatsApp API Status:", response.status_code)
        print("📡 WhatsApp API Response:", response.text)

        response.raise_for_status()
        return True, response.json()

    except requests.exceptions.RequestException as e:
        return False, str(e)
