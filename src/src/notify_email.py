import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

GMAIL_ADDRESS = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
NOTIFY_EMAIL = os.environ["NOTIFY_EMAIL"]

def send_notification(text_data, video_url, caption):
    print("📧 Sende Benachrichtigungs-Mail...")

    kategorie = text_data.get("kategorie", "")
    topic = text_data.get("topic", "")
    text = text_data.get("text", "")
    date = text_data.get("date", "")

    from post_tiktok import KATEGORIE_HASHTAGS
    hashtags = KATEGORIE_HASHTAGS.get(kategorie, "#liebeskummer #herzschmerz #zitate #gefühle #wahreworte")

    body = f"""
🌩 KOPFGEWITTER – {date}
━━━━━━━━━━━━━━━━━━━━━━━━

📌 TITEL
{topic}

━━━━━━━━━━━━━━━━━━━━━━━━
📝 TEXT
{text}

━━━━━━━━━━━━━━━━━━━━━━━━
#️⃣ HASHTAGS
{hashtags}

━━━━━━━━━━━━━━━━━━━━━━━━
🎬 VIDEO
{video_url}

━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ Jetzt auf TikTok posten!
Instagram postet automatisch in 15 Minuten.
"""

    msg = MIMEMultipart()
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = NOTIFY_EMAIL
    msg["Subject"] = f"🌩 Kopfgewitter – Jetzt auf TikTok posten! ({date})"
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        smtp.send_message(msg)

    print(f"✅ Mail gesendet an {NOTIFY_EMAIL}")
