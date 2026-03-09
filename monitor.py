import os, requests, html
from datetime import datetime, timedelta

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Category mapping for Weekly Reviews
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
    today = datetime.now()
    days_since_friday = (today.weekday() - 4) % 7
    latest_friday = today - timedelta(days=days_since_friday)
    fridays = [latest_friday, latest_friday - timedelta(days=7)]
    
    full_report = "<b>📊 BENCHMARK BI-WEEKLY REVIEWS</b>\n"
    full_report += f"Period: {fridays[1].strftime('%d %b')} — {fridays[0].strftime('%d %b %Y')}\n\n"

    # --- 1. BI-WEEKLY CATEGORIES ---
    found_weekly = False
    for name, slug in CATEGORIES.items():
        folder_name = slug if "environmental" in slug else slug.replace('_law_review', '').replace('_law', '')
        links = []
        for fri in fridays:
            date_str = fri.strftime("%d-%m-%Y")
            url = f"https://benchmarkinc.com.au/benchmark/{folder_name}/benchmark_{date_str}_{slug}.pdf"
            if requests.head(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5).status_code == 200:
                links.append(f"  • {fri.strftime('%d %b')}: <a href='{url}'>View PDF</a>")
        if links:
            full_report += f"<b>{name}</b>\n" + "\n".join(links) + "\n\n"
            found_weekly = True

    # --- 2. DAILY UPDATES (LATEST 2 DAYS) ---
    full_report += "<b>🗞️ DAILY BULLETINS (LATEST)</b>\n"
    daily_found = False
    # Check today and yesterday for Daily Civil and Daily Construction
    for i in range(2):
        target_date = today - timedelta(days=i)
        d_str = target_date.strftime("%d-%m-%Y")
        
        # Daily Construction
        const_url = f"https://benchmarkinc.com.au/benchmark/construction/benchmark_{d_str}_construction.pdf"
        # Daily Civil (Composite)
        civil_url = f"https://benchmarkinc.com.au/benchmark/composite/benchmark_{d_str}_insurance_banking_construction_government.pdf"
        
        if requests.head(const_url, timeout=5).status_code == 200:
            full_report += f"• {target_date.strftime('%d %b')}: <a href='{const_url}'>Daily Construction</a>\n"
            daily_found = True
        if requests.head(civil_url, timeout=5).status_code == 200:
            full_report += f"• {target_date.strftime('%d %b')}: <a href='{civil_url}'>Daily Civil (Multi)</a>\n"
            daily_found = True

    if not daily_found: full_report += "<i>No daily updates found for the last 48hrs.</i>\n"

    return full_report if (found_weekly or daily_found) else None

def main():
    if not TELEGRAM_TOKEN or not CHAT_ID: return
    report = check_benchmark()
    if report: send_telegram(report)

if __name__ == "__main__":
    main()
