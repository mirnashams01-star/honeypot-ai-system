# test_alert.py
import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/1504126382631026768/sozLzv1Foc-xkUhpTecwydhXoQepACodjiypsxCkERozIoM_4pkYMm-w_mtS8Mi8_Juj"

message = {
    "embeds": [{
        "title": "🚨 SSH Attack Detected!",
        "color": 15158332,
        "fields": [
            {"name": "🌐 IP", "value": "192.168.1.100", "inline": True},
            {"name": "👤 Username", "value": "root", "inline": True},
            {"name": "🔑 Password", "value": "123456", "inline": True},
            {"name": "📋 Event", "value": "cowrie.login.failed", "inline": True},
            {"name": "⏰ Time", "value": "2026-05-13T10:00:00", "inline": True},
        ],
        "footer": {"text": "SOC Monitoring System"}
    }]
}

requests.post(WEBHOOK_URL, json=message)
print("✅ Alert sent!")