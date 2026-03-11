import os, requests, html
from datetime import datetime, timedelta, timezone # AMENDED

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Melbourne Time Offset (UTC+11)
MELB_TZ = timezone(timedelta(hours=11))

# Category mapping: Display Name -> Filename Slug
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
    # --- AMENDED: Ensure 'today' is Melbourne time ---
    today = datetime.now(MELB_TZ) 
    # -------------------------------------------------
    
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
            except:
                continue

        if category_links:
            full_report += f"<b>{name}</b>\n" + "\n".join(category_links) + "\n\n"
            found_any = True

    return full_report if found_any else None

def main():
    if not TELEGRAM_TOKEN or not CHAT_ID: return
    report = check_benchmark()
    if report:
        send_telegram(report)

if __name__ == "__main__":
    main()
