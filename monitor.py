import os, requests, html
from datetime import datetime, timedelta

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Category mapping: Display Name -> Filename Slug
# Folder names are derived from these slugs automatically in the logic below
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
    # disable_web_page_preview=True ensures a clean list without PDF attachments
    requests.post(url, json={
        "chat_id": CHAT_ID, 
        "text": text, 
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }, timeout=30)

def check_benchmark():
    today = datetime.now()
    # Find the most recent Friday
    days_since_friday = (today.weekday() - 4) % 7
    latest_friday = today - timedelta(days=days_since_friday)
    
    # Dates for the last 2 Fridays
    fridays = [latest_friday, latest_friday - timedelta(days=7)]
    
    full_report = "<b>📊 BENCHMARK BI-WEEKLY REVIEWS</b>\n"
    full_report += f"Period: {fridays[1].strftime('%d %b')} — {fridays[0].strftime('%d %b %Y')}\n\n"

    found_any = False

    for name, slug in CATEGORIES.items():
        # Benchmark's folder names are usually the slug minus '_law' or '_review'
        folder_name = slug.replace('_law_review', '').replace('_law', '')
        
        category_links = []
        for fri in fridays:
            date_str = fri.strftime("%d-%m-%Y")
            # Pattern: https://benchmarkinc.com.au/benchmark/{folder}/benchmark_{date}_{filename_slug}.pdf
            pdf_url = f"https://benchmarkinc.com.au/benchmark/{folder_name}/benchmark_{date_str}_{slug}.pdf"
            
            try:
                # We use a standard User-Agent to avoid being flagged
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                response = requests.head(pdf_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    category_links.append(f"  • {fri.strftime('%d %b')}: <a href='{pdf_url}'>View PDF</a>")
                else:
                    # Fallback check for slight naming variations if HEAD fails
                    print(f"Skipping {name} for {date_str} (Status: {response.status_code})")
            except:
                continue

        if category_links:
            full_report += f"<b>{name}</b>\n" + "\n".join(category_links) + "\n\n"
            found_any = True

    return full_report if found_any else None

def main():
    if not TELEGRAM_TOKEN or not CHAT_ID: 
        print("Error: Missing Telegram Environment Variables")
        return
    
    report = check_benchmark()
    if report:
        send_telegram(report)
    else:
        send_telegram("🧐 <b>Benchmark Update:</b> No new editions found for this period.")

if __name__ == "__main__":
    main()
