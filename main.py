import sys, os, json
from datetime import datetime
from pathlib import Path

Path("output").mkdir(exist_ok=True)
today = datetime.now().strftime("%Y-%m-%d")
print(f"🎬 KOPFGEWITTER – {today}")
sys.path.insert(0, "src")

from generate_text import generate_text
text_data = generate_text()

from generate_voice import generate_voice, get_audio_duration
audio_path = f"output/voice_{today}.mp3"
generate_voice(text_data["text"], audio_path)
duration = get_audio_duration(audio_path)
print(f"⏱️ Dauer: {duration:.1f}s")

from create_video import download_background_video, create_video
bg_path = f"output/background_{today}.mp4"
download_background_video(bg_path, duration)
final_path = f"output/final_{today}.mp4"
create_video(bg_path, audio_path, final_path, duration)

from post_tiktok import generate_caption, post_to_tiktok
caption = generate_caption(text_data)
result = post_to_tiktok(final_path, caption)
with open(f"output/result_{today}.json", "w") as f:
    json.dump(result, f, indent=2)
print(f"✅ FERTIG! Publish ID: {result.get('publish_id', 'N/A')}")
