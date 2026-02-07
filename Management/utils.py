import requests
from django.conf import settings

def send_whatsapp_ticket(mobile_number, overridebot="yes"):
    """
    Sends WhatsApp message using Cunnekt API
    mobile_number format: 91XXXXXXXXXX
    """

    url = settings.WHATSAPP_API_URL

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
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return True, response.json()

    except requests.exceptions.RequestException as e:
        return False, str(e)
