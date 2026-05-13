from flask import Flask, request, render_template
import json
import os
import csv
from datetime import datetime
import requests as req

app = Flask(__name__)
LOG_FILE = "attacks.log"
HACKERS_FILE = "hackers.json"
CSV_FILE = "attacks_for_ai.csv"

# ─────────────────────────────────────────
# الـ Location من الـ IP
# ─────────────────────────────────────────
def get_location(ip):
    try:
        if ip == "127.0.0.1" or ip.startswith("192.168"):
            return {
                "country": "Local Network",
                "city": "localhost",
                "isp": "Local"
            }
        response = req.get(f"http://ip-api.com/json/{ip}", timeout=3)
        data = response.json()
        if data["status"] == "success":
            return {
                "country": data.get("country", "Unknown"),
                "city": data.get("city", "Unknown"),
                "isp": data.get("isp", "Unknown")
            }
    except:
        pass
    return {"country": "Unknown", "city": "Unknown", "isp": "Unknown"}


# ─────────────────────────────────────────
# كشف نوع الهجوم
# ─────────────────────────────────────────
def detect_attack_type(username, password, user_agent):
    attacks_detected = []

    sql_patterns = ["'", '"', "OR", "AND", "--", ";", "1=1", "DROP", "SELECT", "UNION"]
    for p in sql_patterns:
        if p.lower() in username.lower() or p.lower() in password.lower():
            attacks_detected.append("SQL Injection")
            break

    xss_patterns = ["<script>", "javascript:", "onerror", "onload", "alert("]
    for p in xss_patterns:
        if p.lower() in username.lower() or p.lower() in password.lower():
            attacks_detected.append("XSS Attack")
            break

    path_patterns = ["../", "..\\", "/etc/passwd", "/windows/"]
    for p in path_patterns:
        if p.lower() in username.lower() or p.lower() in password.lower():
            attacks_detected.append("Path Traversal")
            break

    cmd_patterns = [";ls", ";dir", "&&", "|", "`", "$("]
    for p in cmd_patterns:
        if p.lower() in username.lower() or p.lower() in password.lower():
            attacks_detected.append("Command Injection")
            break

    bot_patterns = ["python-requests", "curl", "wget", "bot", "spider"]
    for p in bot_patterns:
        if p.lower() in user_agent.lower():
            attacks_detected.append("Bot Attack")
            break

    weak_passwords = ["123456", "password", "admin", "qwerty",
                      "abc123", "111111", "letmein", "1234"]
    if password.lower() in weak_passwords:
        attacks_detected.append("Brute Force")

    if "@" in username and len(password) > 8:
        attacks_detected.append("Credential Stuffing")

    admin_names = ["admin", "root", "administrator", "superuser"]
    if username.lower() in admin_names:
        attacks_detected.append("Broken Authentication")

    if not attacks_detected:
        attacks_detected.append("Unknown Attempt")

    return attacks_detected


# ─────────────────────────────────────────
# حساب الـ Severity
# ─────────────────────────────────────────
def get_severity(attack_types):
    critical = ["SQL Injection", "Command Injection", "Path Traversal"]
    high = ["XSS Attack", "Broken Authentication", "Credential Stuffing"]

    for t in attack_types:
        if t in critical:
            return "CRITICAL"
    for t in attack_types:
        if t in high:
            return "HIGH"
    return "MEDIUM"


# ─────────────────────────────────────────
# حفظ بالـ 3 formats
# ─────────────────────────────────────────
def save_all_formats(data):

    # 1. LOG FILE — للقراءة البشرية
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"""
========================================
TIMESTAMP  : {data['timestamp']}
IP         : {data['ip']}
LOCATION   : {data['location']['city']}, {data['location']['country']}
ISP        : {data['location']['isp']}
USERNAME   : {data['username']}
PASSWORD   : {data['password']}
BROWSER    : {data['browser']}
DEVICE     : {data['device']}
ATTACK     : {', '.join(data['attack_types'])}
SEVERITY   : {data['severity']}
SOURCE     : web_honeypot
========================================\n""")

    # 2. JSON FILE — للـ dashboard
    attacks = []
    json_file = "attacks.json"
    if os.path.exists(json_file):
        with open(json_file, "r") as f:
            try:
                attacks = json.load(f)
            except:
                attacks = []
    attacks.append(data)
    with open(json_file, "w") as f:
        json.dump(attacks, f, indent=2)

    # 3. CSV FILE — للـ AI (Cyber 3)
    file_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "timestamp", "ip", "country", "city", "isp",
                "username", "password", "browser", "device",
                "attack_types", "severity", "source"
            ])
        writer.writerow([
            data["timestamp"],
            data["ip"],
            data["location"]["country"],
            data["location"]["city"],
            data["location"]["isp"],
            data["username"],
            data["password"],
            data["browser"],
            data["device"],
            "|".join(data["attack_types"]),
            data["severity"],
            "web_honeypot"
        ])


# ─────────────────────────────────────────
# تتبع الهاكر
# ─────────────────────────────────────────
def track_hacker(ip, attack_data):
    hackers = {}
    if os.path.exists(HACKERS_FILE):
        with open(HACKERS_FILE, "r") as f:
            try:
                hackers = json.load(f)
            except:
                hackers = {}

    if ip not in hackers:
        hackers[ip] = {
            "ip": ip,
            "location": attack_data["location"],
            "first_seen": attack_data["timestamp"],
            "last_seen": attack_data["timestamp"],
            "total_attempts": 0,
            "attack_types_used": [],
            "usernames_tried": [],
            "passwords_tried": [],
            "timeline": [],
            "threat_level": "LOW 🟢"
        }

    h = hackers[ip]
    h["last_seen"] = attack_data["timestamp"]
    h["total_attempts"] += 1
    h["location"] = attack_data["location"]

    if attack_data["username"] not in h["usernames_tried"]:
        h["usernames_tried"].append(attack_data["username"])
    if attack_data["password"] not in h["passwords_tried"]:
        h["passwords_tried"].append(attack_data["password"])
    for t in attack_data["attack_types"]:
        if t not in h["attack_types_used"]:
            h["attack_types_used"].append(t)

    h["timeline"].append({
        "time": attack_data["timestamp"],
        "username": attack_data["username"],
        "password": attack_data["password"],
        "attack_types": attack_data["attack_types"],
        "severity": attack_data["severity"]
    })

    attempts = h["total_attempts"]
    types = len(h["attack_types_used"])
    if attempts >= 20 or types >= 3:
        h["threat_level"] = "CRITICAL 🔴"
    elif attempts >= 10 or types >= 2:
        h["threat_level"] = "HIGH 🟠"
    elif attempts >= 5:
        h["threat_level"] = "MEDIUM 🟡"
    else:
        h["threat_level"] = "LOW 🟢"

    hackers[ip] = h
    with open(HACKERS_FILE, "w") as f:
        json.dump(hackers, f, indent=2)
    return h


# ─────────────────────────────────────────
# الصفحات
# ─────────────────────────────────────────
@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    user_agent = request.headers.get("User-Agent", "")
    ip = request.remote_addr

    location = get_location(ip)
    attack_types = detect_attack_type(username, password, user_agent)
    severity = get_severity(attack_types)

    # استخراج الـ browser والـ device من الـ user agent
    browser = "Unknown"
    device = "Unknown"
    if "Chrome" in user_agent:
        browser = "Chrome"
    elif "Firefox" in user_agent:
        browser = "Firefox"
    elif "Safari" in user_agent:
        browser = "Safari"
    elif "python" in user_agent.lower():
        browser = "Script/Bot"

    if "Windows" in user_agent:
        device = "Windows"
    elif "Linux" in user_agent:
        device = "Linux"
    elif "Mac" in user_agent:
        device = "MacOS"
    elif "Android" in user_agent:
        device = "Android"
    elif "iPhone" in user_agent:
        device = "iPhone"

    attack_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip": ip,
        "location": location,
        "username": username,
        "password": password,
        "browser": browser,
        "device": device,
        "user_agent": user_agent,
        "attack_types": attack_types,
        "severity": severity,
        "source": "web_honeypot"
    }

    hacker = track_hacker(ip, attack_data)
    save_all_formats(attack_data)

    print(f"\n{'='*50}")
    print(f"🚨 ATTACK — {severity}")
    print(f"   IP      : {ip}")
    print(f"   Location: {location['city']}, {location['country']}")
    print(f"   Username: {username} | Password: {password}")
    print(f"   Types   : {', '.join(attack_types)}")
    print(f"   Threat  : {hacker['threat_level']}")
    print(f"{'='*50}")

    return render_template("login.html")


@app.route("/attacks")
def show_attacks():
    attacks = []
    if os.path.exists("attacks.json"):
        with open("attacks.json", "r") as f:
            try:
                attacks = json.load(f)
            except:
                attacks = []

    total = len(attacks)

    # إحصائيات
    types_count = {}
    severity_count = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0}
    countries = {}

    for a in attacks:
        for t in a.get("attack_types", []):
            types_count[t] = types_count.get(t, 0) + 1
        sev = a.get("severity", "MEDIUM")
        severity_count[sev] = severity_count.get(sev, 0) + 1
        country = a.get("location", {}).get("country", "Unknown")
        countries[country] = countries.get(country, 0) + 1

    types_html = "".join([
        f"<div class='stat'>⚠️ {t}: <strong>{c}</strong></div>"
        for t, c in sorted(types_count.items(), key=lambda x: x[1], reverse=True)
    ])

    countries_html = "".join([
        f"<div class='stat'>🌍 {c}: <strong>{n}</strong></div>"
        for c, n in sorted(countries.items(), key=lambda x: x[1], reverse=True)
    ])

    return f"""
    <html>
    <head>
        <title>Honeypot Dashboard</title>
        <style>
            body{{background:#0a0a0a;color:#fff;font-family:Arial;padding:30px}}
            h1{{color:#e94560}}
            h2{{color:#888;margin-top:30px}}
            .grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:20px 0}}
            .card{{background:#111;padding:24px;border-radius:8px;text-align:center}}
            .card .num{{font-size:42px;font-weight:bold}}
            .critical{{color:#ef4444}}.high{{color:#f97316}}.medium{{color:#eab308}}
            .stat{{background:#111;padding:10px 20px;margin:6px 0;border-left:3px solid #e94560}}
            .cols{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
            pre{{background:#111;padding:20px;color:#0f0;font-size:11px;
                 overflow:auto;border-radius:5px;max-height:400px}}
            a{{color:#e94560}}
        </style>
    </head>
    <body>
        <h1>🍯 Honeypot Dashboard</h1>
        <p><a href='/hackers'>👤 Hackers Profiles</a> |
           <a href='/export'>📥 Export CSV for AI</a></p>

        <div class='grid'>
            <div class='card'>
                <div class='num' style='color:#e94560'>{total}</div>
                <div>Total Attacks</div>
            </div>
            <div class='card'>
                <div class='num critical'>{severity_count['CRITICAL']}</div>
                <div>Critical</div>
            </div>
            <div class='card'>
                <div class='num high'>{severity_count['HIGH']}</div>
                <div>High Severity</div>
            </div>
        </div>

        <div class='cols'>
            <div>
                <h2>⚠️ Attack Types</h2>
                {types_html}
            </div>
            <div>
                <h2>🌍 Attacker Locations</h2>
                {countries_html}
            </div>
        </div>

        <h2>📋 Full Log</h2>
        <pre>{json.dumps(attacks[-20:], indent=2)}</pre>
    </body>
    </html>
    """


@app.route("/hackers")
def show_hackers():
    hackers = {}
    if os.path.exists(HACKERS_FILE):
        with open(HACKERS_FILE, "r") as f:
            try:
                hackers = json.load(f)
            except:
                hackers = {}

    hackers_html = ""
    for ip, h in sorted(hackers.items(),
                        key=lambda x: x[1]["total_attempts"],
                        reverse=True):
        color = "#22c55e"
        if "CRITICAL" in h["threat_level"]:
            color = "#ef4444"
        elif "HIGH" in h["threat_level"]:
            color = "#f97316"
        elif "MEDIUM" in h["threat_level"]:
            color = "#eab308"

        loc = h.get("location", {})
        timeline_html = "".join([
            f"<div class='event'>🕐 {e['time']} | "
            f"<b>{e['username']}</b> / <b>{e['password']}</b> | "
            f"⚠️ {', '.join(e['attack_types'])} | {e['severity']}</div>"
            for e in h["timeline"][-5:]
        ])

        hackers_html += f"""
        <div class='card'>
            <div class='header'>
                <span class='ip'>🌐 {ip}</span>
                <span class='threat' style='background:{color}'>
                    {h['threat_level']}
                </span>
            </div>
            <div class='info'>
                🌍 Location : {loc.get('city','?')}, {loc.get('country','?')}<br>
                🏢 ISP      : {loc.get('isp','?')}<br>
                📅 First    : {h['first_seen']}<br>
                📅 Last     : {h['last_seen']}<br>
                🔢 Attempts : <b>{h['total_attempts']}</b><br>
                ⚠️ Types    : {', '.join(h['attack_types_used'])}<br>
                👤 Usernames: {', '.join(h['usernames_tried'][:5])}<br>
                🔑 Passwords: {', '.join(h['passwords_tried'][:5])}
            </div>
            <div class='tl-title'>📜 Last 5 Actions:</div>
            {timeline_html}
        </div>"""

    return f"""
    <html>
    <head>
        <title>Hackers Profiles</title>
        <style>
            body{{background:#0a0a0a;color:#fff;font-family:Arial;padding:30px}}
            h1{{color:#e94560}}
            .card{{background:#111;border:1px solid #222;
                   border-radius:8px;padding:24px;margin:16px 0}}
            .header{{display:flex;justify-content:space-between;
                     align-items:center;margin-bottom:16px}}
            .ip{{font-size:20px;font-weight:bold}}
            .threat{{padding:6px 16px;border-radius:20px;
                     color:white;font-weight:bold}}
            .info{{color:#aaa;line-height:2;margin-bottom:16px}}
            .tl-title{{color:#e94560;margin-bottom:8px}}
            .event{{background:#1a1a1a;padding:8px 12px;
                    margin:4px 0;border-radius:4px;
                    font-size:12px;color:#888}}
            a{{color:#e94560}}
        </style>
    </head>
    <body>
        <h1>👤 Hackers Profiles</h1>
        <p><a href='/attacks'>← Dashboard</a></p>
        <p>Total Unique IPs: <b style='color:#e94560'>{len(hackers)}</b></p>
        {hackers_html}
    </body>
    </html>
    """


@app.route("/export")
def export_csv():
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        return f"""
        <html>
        <head><style>
            body{{background:#0a0a0a;color:#0f0;font-family:monospace;padding:30px}}
            a{{color:#e94560}}
            pre{{font-size:11px}}
        </style></head>
        <body>
            <h2 style='color:#e94560'>📥 CSV Data for AI Analysis</h2>
            <p><a href='/attacks'>← Back</a></p>
            <p style='color:#888'>Share this data with Cyber 3 for AI analysis</p>
            <pre>{content}</pre>
        </body>
        </html>
        """
    return "No data yet"


if __name__ == "__main__":
    print("🍯 Web Honeypot RUNNING!")
    print("🔗 Login   : http://localhost:5000")
    print("📊 Dashboard: http://localhost:5000/attacks")
    print("👤 Hackers : http://localhost:5000/hackers")
    print("📥 CSV/AI  : http://localhost:5000/export")
    app.run(debug=True, host="0.0.0.0", port=5000)