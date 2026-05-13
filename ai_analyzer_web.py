import csv
import os
import time
import requests
from groq import Groq

GROQ_API_KEY = "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"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1504126382631026768/sozLzv1Foc-xkUhpTecwydhXoQepACodjiypsxCkERozIoM_4pkYMm-w_mtS8Mi8_Juj"

client = Groq(api_key=GROQ_API_KEY)

def analyze_attack(row):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"Analyze this honeypot attack in 2 lines:\nIP: {row.get('ip')}\nAttack: {row.get('attack_types')}\nSeverity: {row.get('severity')}\nUsername: {row.get('username')}"
        }]
    )
    return response.choices[0].message.content

def send_ai_alert(row, analysis):
    message = {
        "embeds": [{
            "title": "🤖 AI Attack Analysis",
            "color": 15105570,
            "fields": [
                {"name": "🌐 IP", "value": row.get("ip", "Unknown"), "inline": True},
                {"name": "⚔️ Attack", "value": row.get("attack_types", "Unknown"), "inline": True},
                {"name": "🔴 Severity", "value": row.get("severity", "Unknown"), "inline": True},
                {"name": "🤖 AI Analysis", "value": analysis[:500], "inline": False},
            ],
            "footer": {"text": "Honeypot AI Monitor"}
        }]
    }
    requests.post(DISCORD_WEBHOOK, json=message)
    print(f"✅ Alert sent for {row.get('ip')}")

def monitor_web_logs(log_path):
    print(f"🤖 AI Monitoring Web: {log_path}")
    last_row_count = 0
    while True:
        try:
            with open(log_path, "r") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                new_rows = rows[last_row_count:]
                for row in new_rows:
                    print(f"🔍 Analyzing: {row.get('ip')}")
                    analysis = analyze_attack(row)
                    send_ai_alert(row, analysis)
                last_row_count = len(rows)
        except Exception as e:
            print(f"❌ Error: {e}")
        time.sleep(2)

monitor_web_logs(r"C:\Users\DELL\OneDrive\Documents\web-honeypot\attacks_for_ai.csv")