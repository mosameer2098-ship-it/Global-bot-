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
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
        res = requests.post(url, json=payload, timeout=10)
        # Yeh line Heroku logs me batayegi ki telegram ka message gaya ya koi error aaya
        dprint(f"[DEBUG] Telegram Response: {res.status_code} - {res.text}")
    except Exception as e:
        dprint(f"[-] Telegram Alert Error: {e}")

def run_bot():
    dprint("[+] Pure API SEO Bot started successfully with Telegram Debug Mode!")
    send_alert("🚀 *API SEO BOT STARTED ON HEROKU*\n\n⚡ Zero browser crashes, live debugging active.")
    
    while True:
        keyword = random.choice(KEYWORDS)
        dprint(f"\n[*] Querying via API for: '{keyword}'")
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        try:
            res = requests.get(f"https://www.google.com/search?q={requests.utils.quote(keyword)}", headers=headers, timeout=15)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                found_target = False
                for a in soup.find_all('a', href=True):
                    if TARGET_DOMAIN in a['href']:
                        found_target = True
                        dprint(f"[+] Target found for keyword: {keyword}")
                        send_alert(f"🎯 *ORGANIC RANK DETECTED (API)*\n\n🔑 **Keyword:** `{keyword}`\n🌐 **Domain:** `{TARGET_DOMAIN}`")
                        break
                
                if not found_target:
                    dprint(f"[-] Keyword '{keyword}' checked (Target not in top search page right now).")
            
            # Simulate Traffic to Target Domain
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
