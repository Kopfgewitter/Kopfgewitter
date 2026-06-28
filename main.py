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
timestamps_path = f"output/voice_{today}_timestamps.json"
generate_voice(text_data["text"], audio_path)
duration = get_audio_duration(audio_path)
print(f"⏱️ Dauer: {duration:.1f}s")
from create_video import download_background_video, create_video
bg_path = f"output/background_{today}.mp4"
download_background_video(bg_path, duration)
final_path = f"output/final_{today}.mp4"
create_video(bg_path, audio_path, final_path, duration, timestamps_path=timestamps_path)
from post_tiktok import generate_caption, post_to_tiktok
caption = generate_caption(text_data)
tiktok_result = post_to_tiktok(final_path, caption)
with open(f"output/result_tiktok_{today}.json", "w") as f:
    json.dump(tiktok_result, f, indent=2)
from post_instagram import post_to_instagram
instagram_result = post_to_instagram(final_path, caption)
with open(f"output/result_instagram_{today}.json", "w") as f:
    json.dump(instagram_result, f, indent=2)
print(f"✅ FERTIG! TikTok: {tiktok_result.get('publish_id', 'N/A')} | Instagram: {instagram_result.get('media_id', 'N/A')}")
