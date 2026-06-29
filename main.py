import sys, os, json, time
from datetime import datetime
from pathlib import Path

Path("output").mkdir(exist_ok=True)
today = datetime.now().strftime("%Y-%m-%d")
print(f"🎬 KOPFGEWITTER – {today}")
sys.path.insert(0, "src")

# 1. Text generieren
from generate_text import generate_text
text_data = generate_text()

# 2. Voice generieren
from generate_voice import generate_voice, get_audio_duration
audio_path = f"output/voice_{today}.mp3"
timestamps_path = f"output/voice_{today}_timestamps.json"
generate_voice(text_data["text"], audio_path)
duration = get_audio_duration(audio_path)
print(f"⏱️ Dauer: {duration:.1f}s")

# 3. Video erstellen
from create_video import download_background_video, create_video
bg_path = f"output/background_{today}.mp4"
download_background_video(bg_path, duration)
final_path = f"output/final_{today}.mp4"
create_video(bg_path, audio_path, final_path, duration, timestamps_path=timestamps_path, text_data=text_data)

# 4. Caption generieren (ohne TikTok Token abhängigkeit)
from post_tiktok import KATEGORIE_HASHTAGS
kategorie = text_data.get("kategorie", "")
hashtags = KATEGORIE_HASHTAGS.get(kategorie, "#liebeskummer #herzschmerz #zitate #gefühle #wahreworte")
caption = f"{text_data['text']}\n\n{hashtags}"
caption = caption[:2200]

# 5. Zu Cloudinary hochladen
from post_instagram import upload_to_cloudinary
video_url = upload_to_cloudinary(final_path)

# 6. E-Mail schicken – SOFORT nach Cloudinary, vor allem anderen
from notify_email import send_notification
send_notification(text_data, video_url, caption)
print("⏳ Warte 15 Minuten vor Instagram-Post...")
time.sleep(900)

# 7. Instagram automatisch posten
from post_instagram import post_to_instagram
try:
    instagram_result = post_to_instagram(final_path, caption, video_url=video_url)
    print(f"✅ Instagram: {instagram_result.get('media_id', 'N/A')}")
except Exception as e:
    print(f"⚠️ Instagram fehlgeschlagen: {e}")
    instagram_result = {"success": False, "error": str(e)}

with open(f"output/result_instagram_{today}.json", "w") as f:
    json.dump(instagram_result, f, indent=2)

print(f"✅ FERTIG!")
