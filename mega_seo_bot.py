import time
import random
import json
import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from threading import Thread

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BOT_TOKEN = "8394173569:AAFRaOEnIsQPKIurSqkoEh3ATcSQK18PlXA"     
CHAT_ID = "-1003969385685"     
TARGET_DOMAIN = "1xsmmpanel.in"               
SIGNUP_URL = f"https://{TARGET_DOMAIN}/signup"
LOGIN_URL = f"https://{TARGET_DOMAIN}/login"
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
    "active_runs": 0,
    "orders_simulated": 0,
    "keyword_rankings_found": 0,
    "last_report_time": time.time(),
    "last_backup_time": time.time(),
    "last_signup_time": 0,
    "target_next_signup_gap": random.randint(60, 300)
}

def dprint(text):
    print(text, flush=True)

def send_telegram_alert(message, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

def send_telegram_document(file_path, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, "rb") as f:
            files = {"document": f}
            data = {"chat_id": CHAT_ID, "caption": caption, "parse_mode": "Markdown"}
            requests.post(url, data=data, files=files, timeout=20)
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

def get_selenium_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # Heroku par chromium binary path set karna zaroori hai
    if os.path.exists("/usr/bin/chromium"):
        options.binary_location = "/usr/bin/chromium"
    elif os.path.exists("/usr/bin/chromium-browser"):
        options.binary_location = "/usr/bin/chromium-browser"
        
    service = Service("/usr/bin/chromedriver") if os.path.exists("/usr/bin/chromedriver") else Service()
    
    try:
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        dprint(f"[-] Driver Error: {e}")
        return None

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
    dprint(f"\n[*] Launching Real Browser for keyword: '{keyword}'...")
    
    driver = get_selenium_driver()
    if not driver:
        return

    try:
        driver.get("https://www.google.com")
        time.sleep(random.uniform(2, 4))
        
        # Google search input box dhoondhna aur keyword type karna
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        for char in keyword:
            search_box.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        
        search_box.send_keys(Keys.RETURN)
        time.sleep(random.uniform(3, 5))
        
        # Search results mein apni website ko dhoondh kar click karna
        found = False
        for page in range(3): # Pehle 3 pages tak check karega
            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                try:
                    href = link.get_attribute("href")
                    if href and TARGET_DOMAIN in href:
                        dprint(f"[+] Found target site in search results! Clicking: {href}")
                        driver.execute_script("arguments[0].scrollIntoView(true);", link)
                        time.sleep(random.uniform(1, 2))
                        link.click()
                        found = True
                        daily_stats["keyword_rankings_found"] += 1
                        send_telegram_alert(f"🎯 *ORGANIC CLICK & RANK DETECTED!*\n\n🔑 **Keyword:** `{keyword}`\n🌐 **Domain:** `{TARGET_DOMAIN}`")
                        break
                except:
                    continue
            if found:
                break
            
            # Agar pehle page par nahi mila, toh 'Next' page par click karo
            try:
                next_btn = driver.find_element(By.ID, "pnnext")
                next_btn.click()
                time.sleep(random.uniform(3, 5))
            except:
                break

        if found:
            # Website par real user ki tarah thodi der rukna aur scroll karna
            time.sleep(random.uniform(6, 12))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(random.uniform(3, 6))
            
            # Services page visit karna
            driver.get(SERVICES_URL)
            time.sleep(random.uniform(5, 8))
            
            # Kabhi-kabhi naya signup bhi simulate karna
            current_time = time.time()
            if current_time - daily_stats["last_signup_time"] >= daily_stats["target_next_signup_gap"]:
                driver.get(SIGNUP_URL)
                time.sleep(random.uniform(2, 4))
                
                uname, uploader_name, uemail, uphone, upass = generate_real_indian_user()
                
                try:
                    driver.find_element(By.NAME, "username").send_keys(uname)
                    driver.find_element(By.NAME, "name").send_keys(uploader_name)
                    driver.find_element(By.NAME, "email").send_keys(uemail)
                    driver.find_element(By.NAME, "telephone").send_keys(uphone)
                    driver.find_element(By.NAME, "password").send_keys(upass)
                    driver.find_element(By.NAME, "password_again").send_keys(upass)
                    
                    terms_chk = driver.find_element(By.NAME, "terms")
                    if not terms_chk.is_selected():
                        terms_chk.click()
                        
                    time.sleep(random.uniform(1, 2))
                    # Submit button click kar sakte hain ya simulate kar sakte hain
                    
                    active_users_db[uname] = {
                        "password": upass, 
                        "created_at": time.time(), 
                        "last_login": time.time()
                    }
                    save_database(active_users_db)
                    daily_stats["new_signups"] += 1
                    daily_stats["last_signup_time"] = current_time
                    daily_stats["target_next_signup_gap"] = random.randint(1800, 3600)
                    send_telegram_alert(f"🚀 *ORGANIC SIGNUP SIMULATED!*\n\n🇮🇳 **User:** `{uploader_name}`")
                except:
                    pass

    except Exception as e:
        dprint(f"[-] Error in worker task: {e}")
    finally:
    try:
            driver.quit()
        except:
            pass

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
                                f"🤖 *SELENIUM SEO BOT STATUS*\n\n"
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

def run_selenium_bot():
    dprint(f"[+] Selenium Headless SEO Bot started for: {TARGET_DOMAIN}")
    listener = Thread(target=telegram_listener_thread, daemon=True)
    listener.start()
    
    send_telegram_alert("🚀 *SELENIUM SEO BOT STARTED ON HEROKU!*\n\n🌐 Real browser automation is now active for Google ranking.")
    
    while True:
        keywords_list = list(DYNAMIC_KEYWORDS_POOL)
        selected_keyword = random.choice(keywords_list)
        
        worker_thread_task(selected_keyword)
        
        sleep_duration = random.uniform(30, 60)
        dprint(f"\n[~] Waiting for {int(sleep_duration)} seconds before next search...")
        time.sleep(sleep_duration)

if __name__ == "__main__":
    run_selenium_bot()
