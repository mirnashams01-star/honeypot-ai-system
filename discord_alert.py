import requests
import json
import time

WEBHOOK_URL = "https://discord.com/api/webhooks/1504126382631026768/sozLzv1Foc-xkUhpTecwydhXoQepACodjiypsxCkERozIoM_4pkYMm-w_mtS8Mi8_Juj"

def send_alert(event):
    # شكل الرسالة
    message = {
        "embeds": [{
            "title": "🚨 SSH Attack Detected!",
            "color": 15158332,  # لون أحمر
            "fields": [
                {"name": "🌐 IP", "value": event.get("src_ip", "Unknown"), "inline": True},
                {"name": "👤 Username", "value": event.get("username", "Unknown"), "inline": True},
                {"name": "🔑 Password", "value": event.get("password", "Unknown"), "inline": True},
                {"name": "📋 Event", "value": event.get("eventid", "Unknown"), "inline": True},
                {"name": "⏰ Time", "value": event.get("timestamp", "Unknown"), "inline": True},
            ],
            "footer": {"text": "SOC Monitoring System"}
        }]
    }
    
    requests.post(WEBHOOK_URL, json=message)

def monitor_logs(log_path):
    print(f"👀 Monitoring: {log_path}")
    
    with open(log_path, "r") as f:
        # روح لآخر الملف
        f.seek(0, 2)
        
        while True:
            line = f.readline()
            if line:
                try:
                    event = json.loads(line)
                    # ابعت alert لو login attempt
                    if "login" in event.get("eventid", ""):
                        send_alert(event)
                        print(f"✅ Alert sent: {event.get('src_ip')}")
                except:
                    pass
            time.sleep(1)

# شغلي المراقبة
monitor_logs("/opt/cowrie/var/log/cowrie/cowrie.json")