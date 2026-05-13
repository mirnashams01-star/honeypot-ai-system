import requests
import json
import time

GROQ_API_KEY = "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"
WEBHOOK_URL = "https://discord.com/api/webhooks/1504126382631026768/sozLzv1Foc-xkUhpTecwydhXoQepACodjiypsxCkERozIoM_4pkYMm-w_mtS8Mi8_Juj"

def analyze_attack(log_data):
    prompt = f"""
    أنت خبير أمن سيبراني. حلل الهجوم ده وقولي:
    1. نوع الهجوم (Brute Force / Scan / Exploit / Malware)
    2. مستوى الخطورة (LOW / MEDIUM / HIGH / CRITICAL)
    3. تنبؤ بالتهديد (جملة واحدة)
    
    البيانات:
    {json.dumps(log_data, indent=2)}
    
    رد بـ JSON فقط:
    {{"attack_type": "...", "severity": "...", "prediction": "..."}}
    """
    
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }
    )
    
    result = response.json()
    analysis = json.loads(result["choices"][0]["message"]["content"])
    return analysis

def send_ai_alert(log_data, analysis):
    colors = {
        "LOW": 3066993,      # أخضر
        "MEDIUM": 16776960,  # أصفر
        "HIGH": 15105570,    # برتقالي
        "CRITICAL": 15158332 # أحمر
    }
    
    color = colors.get(analysis["severity"], 15158332)
    
    message = {
        "embeds": [{
            "title": f"🤖 AI Analysis: {analysis['attack_type']}",
            "color": color,
            "fields": [
                {"name": "🌐 IP", "value": log_data.get("src_ip", "Unknown"), "inline": True},
                {"name": "⚔️ Attack Type", "value": analysis["attack_type"], "inline": True},
                {"name": "🔴 Severity", "value": analysis["severity"], "inline": True},
                {"name": "🔮 Prediction", "value": analysis["prediction"], "inline": False},
                {"name": "👤 Username", "value": log_data.get("username", "Unknown"), "inline": True},
                {"name": "🔑 Password", "value": log_data.get("password", "Unknown"), "inline": True},
            ],
            "footer": {"text": "SOC AI Analyzer | Powered by Groq"}
        }]
    }
    
    requests.post(WEBHOOK_URL, json=message)
    print(f"✅ AI Alert sent: {analysis['attack_type']} - {analysis['severity']}")

def monitor_logs(log_path):
    print(f"🤖 AI Monitoring: {log_path}")
    
    with open(log_path, "r") as f:
        f.seek(0, 2)
        
        while True:
            line = f.readline()
            if line:
                try:
                    event = json.loads(line)
                    if "login" in event.get("eventid", ""):
                        print(f"🔍 Analyzing: {event.get('src_ip')}")
                        analysis = analyze_attack(event)
                        send_ai_alert(event, analysis)
                except Exception as e:
                    print(f"❌ Error: {e}")
            time.sleep(1)

monitor_logs("/opt/cowrie/var/log/cowrie/cowrie.json")