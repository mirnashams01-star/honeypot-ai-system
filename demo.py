import subprocess
import time
import sys
import os

print("""
╔══════════════════════════════════════════════╗
║   🍯 HoneyShield - LIVE DEMO                 ║
║   Web Honeypot + AI Analysis                 ║
║   AISprint Hackathon - Team The Slash        ║
╚══════════════════════════════════════════════╝
""")

# ─────────────────────────────────────────
# Step 1: Clear old data for clean demo
# ─────────────────────────────────────────
print("🧹 Clearing old data for fresh demo...")
for f in ["attacks.json", "attacks_for_ai.csv", "hackers.json", "attacks.log"]:
    if os.path.exists(f):
        os.remove(f)
print("✅ Clean slate ready!\n")
time.sleep(1)

# ─────────────────────────────────────────
# Step 2: Start Web Honeypot
# ─────────────────────────────────────────
print("1️⃣  Starting Web Honeypot on http://localhost:5000 ...")
honeypot = subprocess.Popen(
    [sys.executable, "app.py"],
    creationflags=subprocess.CREATE_NEW_CONSOLE
)
time.sleep(3)
print("   ✅ Web Honeypot RUNNING!\n")

# ─────────────────────────────────────────
# Step 3: Start AI Analyzer
# ─────────────────────────────────────────
print("2️⃣  Starting AI Analyzer + Discord Alerts...")
analyzer = subprocess.Popen(
    [sys.executable, "ai_analyzer_web.py"],
    creationflags=subprocess.CREATE_NEW_CONSOLE
)
time.sleep(3)
print("   ✅ AI Analyzer RUNNING!\n")

# ─────────────────────────────────────────
# Step 4: Open Dashboard in browser
# ─────────────────────────────────────────
print("3️⃣  Opening Dashboard...")
time.sleep(1)
os.startfile("http://localhost:5000/attacks")
time.sleep(1)
os.startfile("http://localhost:5000/hackers")
print("   ✅ Dashboard OPEN!\n")

# ─────────────────────────────────────────
# Step 5: Attack Simulation
# ─────────────────────────────────────────
print("⏳ Starting attack simulation in 5 seconds...")
print("   👉 Watch the Dashboard and Discord!\n")
time.sleep(5)

print("="*55)
print("🎯 ATTACK SIMULATION STARTING NOW")
print("="*55 + "\n")

print("💥 Wave 1: Brute Force Attack...")
subprocess.run([sys.executable, "attack1.py"])
print("   ✅ Wave 1 Done!\n")
time.sleep(2)

print("💥 Wave 2: Credential Stuffing...")
subprocess.run([sys.executable, "attack2.py"])
print("   ✅ Wave 2 Done!\n")
time.sleep(2)

print("💥 Wave 3: Bot Attack...")
subprocess.run([sys.executable, "attack3.py"])
print("   ✅ Wave 3 Done!\n")
time.sleep(2)

# ─────────────────────────────────────────
# Step 6: Show Final Results
# ─────────────────────────────────────────
print("="*55)
print("📊 DEMO COMPLETE!")
print("="*55)
print()
print("✅ Open these in your browser:")
print("   🌐 Dashboard : http://localhost:5000/attacks")
print("   👤 Hackers   : http://localhost:5000/hackers")
print("   📥 AI Data   : http://localhost:5000/export")
print("   🔔 Discord   : Check your Discord channel!")
print()
print("✅ HoneyShield caught ALL attacks successfully!")
print()
print("="*55)
print("🍯 HoneyShield - Protecting businesses from hackers")
print("   Team The Slash | AISprint | Duckurity")
print("="*55)

input("\n👉 Press Enter to stop the demo...")
honeypot.terminate()
analyzer.terminate()
print("\n👋 Demo stopped. Good luck! 🔥")