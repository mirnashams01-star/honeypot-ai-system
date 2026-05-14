import requests
import json

GROQ_API_KEY = "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"
WEBHOOK_URL = "https://discord.com/api/webhooks/1504126382631026768/sozLzv1Foc-xkUhpTecwydhXoQepACodjiypsxCkERozIoM_4pkYMm-w_mtS8Mi8_Juj"

# log تجريبي
test_log = {
    "eventid": "cowrie.login.failed",
    "src_ip": "192.168.1.100",
    "username": "root",
    "password": "123456",
    "timestamp": "2026-05-13T10:00:00"
}

# تحليل AI
def analyze_attack(log_data):
    prompt = f"""
    أنت خبير أمن سيبراني. حلل الهجوم ده وقولي:
    1. نوع الهجوم (Brute Force / Scan / Exploit / Malware)
    2. مستوى الخطورة (LOW / MEDIUM / HIGH / CRITICAL)
    3. تنبؤ بالتهديد (جملة واحدة)
    
    البيانات: {json.dumps(log_data)}
    
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
    print(f"API Response: {result}") 
    return json.loads(result["choices"][0]["message"]["content"])

# اختبار
print("🔍 Analyzing...")
analysis = analyze_attack(test_log)
print(f"✅ Result: {analysis}")

# بعت على Discord
colors = {"LOW": 3066993, "MEDIUM": 16776960, "HIGH": 15105570, "CRITICAL": 15158332}
message = {
    "embeds": [{
        "title": f"🤖 AI Analysis: {analysis['attack_type']}",
        "color": colors.get(analysis["severity"], 15158332),
        "fields": [
            {"name": "⚔️ Attack Type", "value": analysis["attack_type"], "inline": True},
            {"name": "🔴 Severity", "value": analysis["severity"], "inline": True},
            {"name": "🔮 Prediction", "value": analysis["prediction"], "inline": False},
        ],
        "footer": {"text": "SOC AI Analyzer | Powered by Groq"}
    }]
}
requests.post(WEBHOOK_URL, json=message)
print("✅ Discord Alert sent!")