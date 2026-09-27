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

TIER1_TARGET_KEYWORDS = [
    "1xsmmpanel", "1x smm panel", "1xsmmpanel.in cheapest",
    "1xsmmpanel india", "1xsmmpanel services", "1xsmmpanel login", "1xsmmpanel signup",
    "cheap smm panel for instagram india", "fast smm panel india", "automated smm panel india",
    "trusted smm panel with upi", "instant smm panel paytm", "indian smm panel with phonepe",
    "cheap instagram followers upi panel", "buy telegram members cheap panel india",
    "youtube watchtime cheap panel india", "instagram likes instant delivery panel india"
]

DYNAMIC_KEYWORDS_POOL = set(TIER1_TARGET_KEYWORDS)

daily_stats = {
    "total_searches": 0,
    "new_signups": 0,
    "keyword_rankings_found": 0,
    "last_signup_time": 0,
    "target_next_signup_gap": random.randint(60, 300)
}

def dprint(text):
    print(text, flush=True)

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

def load_database():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_database(db):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(db, f, indent=4)
    except:
        pass

active_users_db = load_database()

def generate_real_indian_user():
    first_names = ["rahul", "amit", "rohit", "vikash", "manish", "sandeep", "ajay", "vijay", "deepak", "kunal", "sachin", "abhishek", "vivek", "pankaj", "sunil", "priya", "pooja", "neha", "divya", "anjali"]
    surnames = ["sharma", "verma", "kumar", "singh", "patel", "gupta", "yadav", "mishra", "shukla", "tiwari", "pandey", "dubey", "jain", "agrawal", "rajput"]
    
    f_name = random.choice(first_names).lower()
    l_name = random.choice(surnames).lower()
    rand_num = random.randint(10, 999)
    username = f"{f_name}_{l_name}{rand_num}"
    fullname = f"{f_name.capitalize()} {l_name.capitalize()}"
    email = f"{f_name}.{l_name}{rand_num}@gmail.com"
    phone = f"9{random.randint(100000000, 999999999)}"
    password = f"Ind@{random.randint(1000,9999)}#!"
    return username, fullname, email, phone, password

def worker_thread_task(keyword):
    global daily_stats
    daily_stats["total_searches"] += 1
    dprint(f"\n[*] Executing Fast API Request for keyword: '{keyword}'...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,hi;q=0.8"
    }
    
    try:
        # Google Search via Requests
        search_url = f"https://www.google.com/search?q={requests.utils.quote(keyword)}"
        response = requests.get(search_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            found = False
            
            for a in soup.find_all('a', href=True):
                href = a['href']
                if TARGET_DOMAIN in href:
                    found = True
                    daily_stats["keyword_rankings_found"] += 1
                    dprint(f"[+] Target found in search results for: {keyword}")
                    send_telegram_alert(f"🎯 *ORGANIC RANK DETECTED (API MODE)*\n\n🔑 **Keyword:** `{keyword}`\n🌐 **Domain:** `{TARGET_DOMAIN}`")
                    break
            
            # Simulate Traffic & Signup if target is checked
            time.sleep(random.uniform(2, 4))
            requests.get(f"https://{TARGET_DOMAIN}", headers=headers, timeout=10)
            requests.get(SERVICES_URL, headers=headers, timeout=10)
            
            current_time = time.time()
            if current_time - daily_stats["last_signup_time"] >= daily_stats["target_next_signup_gap"]:
                uname, uploader_name, uemail, uphone, upass = generate_real_indian_user()
                signup_payload = {
                    "username": uname,
                    "name": uploader_name,
                    "email": uemail,
                    "telephone": uphone,
                    "password": upass,
                    "password_again": upass,
                    "terms": "on"
                }
                
                reg_res = requests.post(SIGNUP_URL, data=signup_payload, headers=headers, timeout=10)
                if reg_res.status_code == 200 or reg_res.history:
                    active_users_db[uname] = {
                        "password": upass, 
                        "created_at": time.time(), 
                        "last_login": time.time()
                    }
                    save_database(active_users_db)
                    daily_stats["new_signups"] += 1
                    daily_stats["last_signup_time"] = current_time
                    daily_stats["target_next_signup_gap"] = random.randint(1800, 3600)
                    send_telegram_alert(f"🚀 *ORGANIC SIGNUP SIMULATED (API)*\n\n🇮🇳 **User:** `{uploader_name}`")
        else:
            dprint(f"[-] Search Engine returned status code: {response.status_code}")
            
    except Exception as e:
        dprint(f"[-] API Worker Error: {e}")

def telegram_listener_thread():
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=30"
            res = requests.get(url, timeout=35)
            if res.status_code == 200:
                data = res.json()
                for result in data.get("result", []):
                    offset = result["update_id"] + 1
                    if "callback_query" in result:
                        cq = result["callback_query"]
                        query_id = cq["id"]
                        data_val = cq["data"]
                        if data_val == "get_status":
                            status_text = (
                                f"🤖 *API SEO BOT STATUS*\n\n"
                                f"🔑 **Active Keywords:** `{len(DYNAMIC_KEYWORDS_POOL)}`\n"
                                f"🏆 **Rank Detections:** `{daily_stats['keyword_rankings_found']}`\n"
                                f"🔍 **Total Searches:** `{daily_stats['total_searches']}`\n"
                                f"🚀 **New Signups:** `{daily_stats['new_signups']}`"
                            )
                            ans_url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
                            requests.post(ans_url, json={"callback_query_id": query_id, "text": "Status Refreshed!"})
                            send_telegram_alert(status_text)
        except:
            pass
        time.sleep(2)

def run_api_bot():
    dprint(f"[+] Lightweight Requests SEO Bot started for: {TARGET_DOMAIN}")
    listener = Thread(target=telegram_listener_thread, daemon=True)
    listener.start()
    
    send_telegram_alert("🚀 *LIGHTWEIGHT API SEO BOT STARTED ON HEROKU*\n\n⚡ Zero browser crashes, high performance mode active.")
    
    while True:
        keywords_list = list(DYNAMIC_KEYWORDS_POOL)
        selected_keyword = random.choice(keywords_list)
        
        worker_thread_task(selected_keyword)
        
        sleep_duration = random.uniform(20, 40)
        dprint(f"\n[~] Waiting for {int(sleep_duration)} seconds before next API hit...")
        time.sleep(sleep_duration)

if __name__ == "__main__":
    run_api_bot()
