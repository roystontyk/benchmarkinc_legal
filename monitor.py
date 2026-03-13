import os, requests, html
from datetime import datetime, timedelta, timezone

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
RUN_MODE = os.getenv("RUN_MODE") # 'summary' or 'cases'

# Melbourne Time Offset (UTC+11)
MELB_TZ = timezone(timedelta(hours=11))

CATEGORIES = {
    "⚖️ CONSTRUCTION": "weekly_construction_law_review",
    "🏦 BANKING": "weekly_banking_law_review",
    "💼 BUSINESS": "weekly_business_law",
    "🏢 CORPORATE GOV": "weekly_corporate_governance",
    "🌱 ENVIRONMENTAL": "weekly_environmental_law"
}

def send_telegram(text):
    if not text: return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID, 
        "text": text, 
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }, timeout=30)

def check_benchmark():
    today = datetime.now(MELB_TZ) 
    
    # --- PART 1: BI-WEEKLY LOGIC (Always included in manual run) ---
    days_since_friday = (today.weekday() - 4) % 7
    latest_friday = today - timedelta(days=days_since_friday)
    fridays = [latest_friday, latest_friday - timedelta(days=7)]
    
    full_report = "<b>📊 BENCHMARK BI-WEEKLY REVIEWS</b>\n"
    full_report += f"Period: {fridays[1].strftime('%d %b')} — {fridays[0].strftime('%d %b %Y')}\n\n"
    found_any = False

    for name, slug in CATEGORIES.items():
        if "environmental" in slug:
            folder_name = slug
        else:
            folder_name = slug.replace('_law_review', '').replace('_law', '')
            
        category_links = []
        for fri in fridays:
            date_str = fri.strftime("%d-%m-%Y")
            pdf_url = f"https://benchmarkinc.com.au/benchmark/{folder_name}/benchmark_{date_str}_{slug}.pdf"
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.head(pdf_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    category_links.append(f"  • {fri.strftime('%d %b')}: <a href='{pdf_url}'>View PDF</a>")
            except: continue

        if category_links:
            full_report += f"<b>{name}</b>\n" + "\n".join(category_links) + "\n\n"
            found_any = True

    # --- PART 2: DAILY ADDITIONS (Only if 'cases' is selected) ---
    if RUN_MODE == "cases":
        daily_date = today.strftime("%d-%m-%Y")
        daily_section = f"🏛️ <b>DAILY ADDITIONS ({today.strftime('%d %b')})</b>\n"
        found_daily = False

        for name, slug in CATEGORIES.items():
            # Extract basic slug for daily URL
            short_slug = slug.replace('weekly_', '').replace('_law_review', '').replace('_law', '')
            daily_folder = "environmental" if "environmental" in short_slug else short_slug
            
            daily_url = f"https://benchmarkinc.com.au/benchmark/{daily_folder}/benchmark_{daily_date}_{short_slug}.pdf"
            
            try:
                if requests.head(daily_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5).status_code == 200:
                    daily_section += f"  • {name}: <a href='{daily_url}'>Daily PDF</a>\n"
                    found_daily = True
            except: continue
        
        if found_daily:
            full_report += "--------------------------\n" + daily_section
        else:
            full_report += "--------------------------\n" + f"🏛️ No daily additions found for {today.strftime('%d %b')}."

    return full_report if found_any else None

def main():
    if not TELEGRAM_TOKEN or not CHAT_ID: return
    report = check_benchmark()
    if report:
        send_telegram(report)

if __name__ == "__main__":
    main()
