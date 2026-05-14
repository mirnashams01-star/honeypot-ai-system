#!/bin/bash

# ============================================
#   Honeypot Demo Script - Cyber 1 (SSH)
# ============================================

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔══════════════════════════════════════╗"
echo "║     SSH Honeypot Demo - Cyber 1      ║"
echo "╚══════════════════════════════════════╝"
echo -e "${NC}"

# ── Step 1: Check dependencies ──
echo -e "${YELLOW}[1/5] Checking dependencies...${NC}"
command -v python3 >/dev/null || { echo -e "${RED}[!] python3 not found${NC}"; exit 1; }
command -v git     >/dev/null || { echo -e "${RED}[!] git not found${NC}"; exit 1; }
echo -e "${GREEN}[✓] Dependencies OK${NC}"

# ── Step 2: Setup Cowrie ──
echo -e "${YELLOW}[2/5] Setting up Cowrie...${NC}"
if [ ! -d "/opt/cowrie" ]; then
    sudo git clone https://github.com/cowrie/cowrie.git /opt/cowrie
    sudo chown -R $USER:$USER /opt/cowrie
fi

cd /opt/cowrie
if [ ! -d "cowrie-env" ]; then
    python3 -m venv cowrie-env
    source cowrie-env/bin/activate
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    pip install -q -e .
else
    source cowrie-env/bin/activate
fi

# ── Step 3: Configure ──
echo -e "${YELLOW}[3/5] Configuring Cowrie...${NC}"
if [ ! -f "etc/cowrie.cfg" ]; then
    cp etc/cowrie.cfg.dist etc/cowrie.cfg
    sed -i 's/^#listen_endpoints.*/listen_endpoints = tcp:2222:interface=0.0.0.0/' etc/cowrie.cfg
    sed -i 's/^hostname =.*/hostname = svr04/' etc/cowrie.cfg
fi
mkdir -p var/log/cowrie
echo -e "${GREEN}[✓] Config ready${NC}"

# ── Step 4: Start Cowrie ──
echo -e "${YELLOW}[4/5] Starting Cowrie...${NC}"
cowrie start 2>/dev/null
sleep 2
if cowrie status | grep -q "running"; then
    echo -e "${GREEN}[✓] Cowrie is running on port 2222${NC}"
else
    echo -e "${RED}[!] Cowrie failed to start${NC}"
    exit 1
fi

# ── Step 5: Run Demo Attack ──
echo -e "${YELLOW}[5/5] Running demo attack...${NC}"
echo ""
echo -e "${BLUE}Opening logs in background...${NC}"
tail -f /opt/cowrie/var/log/cowrie/cowrie.log &
LOG_PID=$!
sleep 1

echo ""
echo -e "${RED}[ATTACK] Starting SSH brute-force...${NC}"
if command -v hydra >/dev/null; then
    hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://127.0.0.1:2222 -t 4 -f 2>/dev/null &
    HYDRA_PID=$!
    sleep 10
    kill $HYDRA_PID 2>/dev/null
else
    # fallback: manual SSH attempts
    for pass in "123456" "password" "admin" "root" "qwerty"; do
        sshpass -p "$pass" ssh -p 2222 -o StrictHostKeyChecking=no root@127.0.0.1 exit 2>/dev/null
        sleep 1
    done
fi

kill $LOG_PID 2>/dev/null

# ── Show Results ──
echo ""
echo -e "${GREEN}╔══════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           Demo Results               ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}Total events logged:${NC}"
wc -l < /opt/cowrie/var/log/cowrie/cowrie.json

echo ""
echo -e "${YELLOW}Attack summary:${NC}"
grep -o '"eventid":"[^"]*"' /opt/cowrie/var/log/cowrie/cowrie.json | sort | uniq -c | sort -rn

echo ""
echo -e "${YELLOW}Passwords attempted:${NC}"
grep -o '"password":"[^"]*"' /opt/cowrie/var/log/cowrie/cowrie.json | sort | uniq -c | sort -rn | head -5

echo ""
echo -e "${YELLOW}Latest log entries:${NC}"
tail -3 /opt/cowrie/var/log/cowrie/cowrie.json | python3 -m json.tool 2>/dev/null || tail -3 /opt/cowrie/var/log/cowrie/cowrie.json

echo ""
echo -e "${GREEN}[✓] Demo complete!${NC}"
echo -e "${BLUE}Full logs: /opt/cowrie/var/log/cowrie/cowrie.json${NC}"
