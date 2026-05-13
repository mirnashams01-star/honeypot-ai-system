#!/usr/bin/env python3
import json
import geoip2.database
import os
from datetime import datetime

COWRIE_LOG = "/opt/cowrie/var/log/cowrie/cowrie.json"
GEOIP_DB   = "/opt/cowrie/etc/geoip/GeoLite2-City.mmdb"
OUTPUT     = "/opt/cowrie/var/log/cowrie/cowrie_enriched.json"

def get_location(ip, reader):
    try:
        r = reader.city(ip)
        return {
            "country": r.country.name or "Unknown",
            "city":    r.city.name    or "Unknown",
            "isp":     "Unknown"
        }
    except Exception:
        if ip.startswith("127.") or ip.startswith("192.168.") or ip.startswith("10."):
            return {"country": "Local Network", "city": "localhost", "isp": "Local"}
        return {"country": "Unknown", "city": "Unknown", "isp": "Unknown"}

def get_attack_type(event):
    eid = event.get("eventid", "")
    pwd = event.get("password", "").lower()
    usr = event.get("username", "").lower()

    types = []
    if "login" in eid:
        types.append("Brute Force")
        if any(p in pwd for p in ["123456", "password", "admin", "qwerty", "abc123"]):
            types.append("Credential Stuffing")
        if "@" in usr:
            types.append("Broken Authentication")
        if not types:
            types.append("Bot Attack")
    elif "command" in eid:
        cmd = event.get("input", "").lower()
        if any(x in cmd for x in ["wget", "curl", "chmod", "bash", "sh"]):
            types.append("Malware Execution")
        else:
            types.append("Command Injection")
    elif "connect" in eid:
        types.append("Bot Attack")

    return types if types else ["Unknown"]

def get_severity(event, attempt_count):
    eid = event.get("eventid", "")
    if "success" in eid:
        return "CRITICAL"
    elif attempt_count > 50:
        return "HIGH"
    elif attempt_count > 10:
        return "MEDIUM"
    else:
        return "LOW"

def main():
    if not os.path.exists(COWRIE_LOG):
        print(f"[!] Log file not found: {COWRIE_LOG}")
        return

    reader = geoip2.database.Reader(GEOIP_DB)

    ip_counts = {}
    enriched  = []

    with open(COWRIE_LOG, "r") as f:
        lines = f.readlines()

    # count attempts per IP
    for line in lines:
        try:
            e = json.loads(line.strip())
            ip = e.get("src_ip", "")
            if ip:
                ip_counts[ip] = ip_counts.get(ip, 0) + 1
        except Exception:
            continue

    # enrich each event
    for line in lines:
        try:
            e = json.loads(line.strip())
            ip  = e.get("src_ip", "Unknown")
            ts  = e.get("timestamp", "")

            # format timestamp
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                ts_fmt = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                ts_fmt = ts

            enriched.append({
                "timestamp":    ts_fmt,
                "ip":           ip,
                "location":     get_location(ip, reader),
                "username":     e.get("username", ""),
                "password":     e.get("password", ""),
                "browser":      "SSH Client",
                "device":       "Unknown",
                "user_agent":   e.get("client_version", "SSH/2.0"),
                "attack_types": get_attack_type(e),
                "severity":     get_severity(e, ip_counts.get(ip, 0)),
                "source":       "ssh_honeypot",
                "eventid":      e.get("eventid", ""),
                "session":      e.get("session", ""),
                "protocol":     e.get("protocol", "ssh")
            })
        except Exception:
            continue

    reader.close()

    with open(OUTPUT, "w") as f:
        json.dump(enriched, f, indent=2)

    print(f"[+] Done! {len(enriched)} events enriched")
    print(f"[+] Output: {OUTPUT}")

    # print sample
    if enriched:
        print("\n[Sample]")
        print(json.dumps(enriched[-1], indent=2))

if __name__ == "__main__":
    main()
