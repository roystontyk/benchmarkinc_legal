import os, requests, html
from datetime import datetime, timedelta, timezone

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

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
    try:
        res = requests.post(url, json={
            "chat_id": CHAT_ID, 
            "text": text, 
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }, timeout=20)
        res.raise_for_status()
    except Exception as e:
        print(f"Telegram Error: {e}")

def check_url(url):
    """Robust check for PDF existence"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/pdf"
    }
    try:
        # Using GET with stream=True is often more reliable than HEAD on some servers
        response = requests.get(url, headers=headers, timeout=10, stream=True)
        return response.status_code == 200
    except:
        return False

def check_benchmark():
    today = datetime.now(MELB_TZ) 
    print(f"Running scan for {today.strftime('%Y-%m-%d %H:%M')}")
    
    # --- PART 1: BI-WEEKLY LOGIC ---
    days_since_friday = (today.weekday() - 4) % 7
    latest_friday = today - timedelta(days=days_since_friday)
    fridays = [latest_friday, latest_friday - timedelta(days=7)]
    
    full_report = "<b>📊 BENCHMARK BI-WEEKLY REVIEWS</b>\n"
    full_report += f"Period: {fridays[1].strftime('%d %b')} — {fridays[0].strftime('%d %b %Y')}\n\n"
    found_any = False

    for name, slug in CATEGORIES.items():
        folder_name = slug if "environmental" in slug else slug.replace('_law_review', '').replace('_law', '')
        category_links = []
        
        for fri in fridays:
            date_str = fri.strftime("%d-%m-%Y")
            pdf_url = f"https://benchmarkinc.com.au/benchmark/{folder_name}/benchmark_{date_str}_{slug}.pdf"
            print(f"Checking Weekly: {pdf_url}")
            if check_url(pdf_url):
                category_links.append(f"  • {fri.strftime('%d %b')}: <a href='{pdf_url}'>View PDF</a>")

        if category_links:
            full_report += f"<b>{name}</b>\n" + "\n".join(category_links) + "\n\n"
            found_any = True

    # --- PART 2: DAILY ADDITIONS ---
    daily_date = today.strftime("%d-%m-%Y")
    daily_section = f"🏛️ <b>DAILY ADDITIONS ({today.strftime('%d %b')})</b>\n"
    found_daily = False

    for name, slug in CATEGORIES.items():
        short_slug = slug.replace('weekly_', '').replace('_law_review', '').replace('_law', '')
        daily_folder = "environmental" if "environmental" in short_slug else short_slug
        daily_url = f"https://benchmarkinc.com.au/benchmark/{daily_folder}/benchmark_{daily_date}_{short_slug}.pdf"
        
        print(f"Checking Daily: {daily_url}")
        if check_url(daily_url):
            daily_section += f"  • {name}: <a href='{daily_url}'>Daily PDF</a>\n"
            found_daily = True
    
    if found_daily:
        full_report += "--------------------------\n" + daily_section
    else:
        full_report += "--------------------------\n" + f"🏛️ No daily additions found for {today.strftime('%d %b')}."

    # Always return something so the user knows the bot is alive
    return full_report

def main():
    if not TELEGRAM_TOKEN or not CHAT_ID: 
        print("Missing Environment Variables")
        return
    report = check_benchmark()
    send_telegram(report)

if __name__ == "__main__":
    main()
