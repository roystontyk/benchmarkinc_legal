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
        "disable_web_page_preview": False # Enable preview so you see the PDF icon
    }, timeout=30)

def check_for_weekly_review():
    # Benchmark usually publishes on Fridays. 
    # Let's find the most recent Friday date.
    today = datetime.now()
    offset = (today.weekday() - 4) % 7
    last_friday = today - timedelta(days=offset)
    date_str = last_friday.strftime("%d-%m-%Y")
    
    # Predict the URL structure
    pdf_url = f"https://benchmarkinc.com.au/benchmark/weekly_construction/benchmark_{date_str}_weekly_construction_law_review.pdf"
    
    print(f"🔍 Checking for Benchmark Review: {date_str}")
    
    try:
        # We only need the headers to see if the file exists (saves data)
        response = requests.head(pdf_url, timeout=15)
        
        if response.status_code == 200:
            msg = (
                f"⚖️ <b>Benchmark Weekly Law Review</b>\n"
                f"📅 Edition: {last_friday.strftime('%d %b %Y')}\n\n"
                f"The latest construction law summary is now available.\n\n"
                f"🔗 <a href='{pdf_url}'>Click to Open PDF</a>"
            )
            return msg
        else:
            return None
    except Exception as e:
        print(f"Benchmark error: {e}")
        return None

def main():
    if not TELEGRAM_TOKEN or not CHAT_ID: return
    
    report = check_for_weekly_review()
    if report:
        send_telegram(report)
    else:
        print("No new edition found yet.")

if __name__ == "__main__":
    main()
