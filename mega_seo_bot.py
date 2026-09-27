import time
import random
import json
import os
import requests
from bs4 import BeautifulSoup
from threading import Thread

BOT_TOKEN = "8394173569:AAFRaOEnIsQPKIurSqkoEh3ATcSQK18PlXA"     
CHAT_ID = "-1003969385685"     
TARGET_DOMAIN = "1xsmmpanel.in"               
SIGNUP_URL = f"https://{TARGET_DOMAIN}/signup"
SERVICES_URL = f"https://{TARGET_DOMAIN}/services"
DB_FILE = "users_db.json"

KEYWORDS = [
    "1xsmmpanel", "1x smm panel", "1xsmmpanel.in cheapest",
    "1xsmmpanel india", "1xsmmpanel services", "1xsmmpanel login"
]

def dprint(text):
    print(text, flush=True)

def send_alert(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except:
        pass

def run_bot():
    dprint("[+] Lightweight API SEO Bot started successfully!")
    send_alert("🚀 *API SEO BOT STARTED ON HEROKU* (Zero Browser Crashes)")
    
    while True:
        keyword = random.choice(KEYWORDS)
        dprint(f"\n[*] Searching keyword via API: '{keyword}'")
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        try:
            res = requests.get(f"https://www.google.com/search?q={requests.utils.quote(keyword)}", headers=headers, timeout=15)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                for a in soup.find_all('a', href=True):
                    if TARGET_DOMAIN in a['href']:
                        dprint(f"[+] Target found for keyword: {keyword}")
                        send_alert(f"🎯 *RANK FOUND (API)*\n🔑 Keyword: `{keyword}`")
                        break
            
            # Hit target site to simulate traffic
            requests.get(f"https://{TARGET_DOMAIN}", headers=headers, timeout=10)
            requests.get(SERVICES_URL, headers=headers, timeout=10)
            dprint("[+] Traffic simulated successfully.")
        except Exception as e:
            dprint(f"[-] Error: {e}")
            
        wait_time = random.uniform(30, 60)
        dprint(f"[~] Waiting for {int(wait_time)} seconds...")
        time.sleep(wait_time)

if __name__ == "__main__":
    run_bot()
