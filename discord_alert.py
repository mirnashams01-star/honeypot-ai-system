import csv
import os
import time
import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/1504126382631026768/sozLzv1Foc-xkUhpTecwydhXoQepACodjiypsxCkERozIoM_4pkYMm-w_mtS8Mi8_Juj"

def monitor_web_logs(log_path):
    print(f"👀 Monitoring Web: {log_path}")
    
    last_row_count = 0
    
    while True:
        try:
            with open(log_path, "r") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            new_rows = rows[last_row_count:]
            
            for row in new_rows:
                message = {
                    "embeds": [{
                        "title": "🌐 Web Attack Detected!",
                        "color": 15105570,
                        "fields": [
                            {"name": "🌐 IP", "value": row.get("ip", "Unknown"), "inline": True},
                            {"name": "👤 Username", "value": row.get("username", "Unknown"), "inline": True},
                            {"name": "🔑 Password", "value": row.get("password", "Unknown"), "inline": True},
                            {"name": "⚔️ Attack Type", "value": row.get("attack_types", "Unknown"), "inline": True},
                            {"name": "🔴 Severity", "value": row.get("severity", "Unknown"), "inline": True},
                            {"name": "⏰ Time", "value": row.get("timestamp", "Unknown"), "inline": True},
                        ],
                        "footer": {"text": "SOC Monitoring System"}
                    }]
                }
                requests.post(WEBHOOK_URL, json=message)
                print(f"✅ Web Alert sent: {row.get('ip')}")
            
            last_row_count = len(rows)
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(2)


monitor_web_logs(r"C:\Users\DELL\OneDrive\Documents\web-honeypot\attacks_for_ai.csv")