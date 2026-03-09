import os, requests, html
from datetime import datetime, timedelta

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(text):
    if not text: return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID, 
        "text": text, 
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }, timeout=30)

def check_weeks():
    today = datetime.now()
    # Find the most recent Friday
    days_since_friday = (today.weekday() - 4) % 7
    latest_friday = today - timedelta(days=days_since_friday)
    
    # Calculate dates for the last 2 Fridays
    fridays = [latest_friday, latest_friday - timedelta(days=7)]
    
    results = []
    
    for fri in fridays:
        date_str = fri.strftime("%d-%m-%Y")
        pdf_url = f"https://benchmarkinc.com.au/benchmark/weekly_construction/benchmark_{date_str}_weekly_construction_law_review.pdf"
        
        # Check if the file exists
        response = requests.head(pdf_url, timeout=15)
        if response.status_code == 200:
            results.append(f"📅 <b>Edition: {fri.strftime('%d %b %Y')}</b>\n🔗 <a href='{pdf_url}'>Open PDF</a>")
    
    return results

def main():
    if not TELEGRAM_TOKEN or not CHAT_ID: return
    
    editions = check_weeks()
    
    if editions:
        header = "⚖️ <b>Benchmark Construction Law: Recent Editions</b>\n\n"
        body = "\n\n".join(editions)
        send_telegram(header + body)
    else:
        print("No recent editions found.")

if __name__ == "__main__":
    main()
