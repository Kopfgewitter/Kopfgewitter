import os, subprocess, requests, random, json
from datetime import datetime
from pathlib import Path

PEXELS_API_KEY = os.environ["PEXELS_API_KEY"]
CACHE_PATH = "used_videos.json"

VIDEO_TERMS = [
    "woman crying emotional close up",
    "person walking alone rain",
    "couple breaking up emotional",
    "woman looking window sad",
    "man emotional breakdown crying",
    "person sitting alone night",
    "emotional woman portrait tears",
    "cinematic emotional people",
    "lonely person dark room",
    "woman thinking night window",
    "sad man sitting alone",
    "emotional couple distance",
    "person crying bedroom",
    "melancholic woman portrait",
    "heartbreak emotional scene",
]

def load_cache():
    if Path(CACHE_PATH).exists():
        with open(CACHE_PATH) as f:
            return json.load(f)
    return []

def save_cache(cache):
    with open(CACHE_PATH, "w") as f:
        json.dump(cache[-50:], f, indent=2)

def download_background_video(output_path, duration):
    cache = load_cache()
    all_videos = []
    terms = random.sample(VIDEO_TERMS, min(3, len(VIDEO_TERMS)))

    headers = {"Authorization": PEXELS_API_KEY}
    for term in terms:
        print(f"🎬 Suche Video: '{term}'")
        r = requests.get("https://api.pexels.com/videos/search", headers=headers,
            params={"query": term, "orientation": "portrait", "size": "medium", "per_page": 15})
        if r.status_code == 200:
            all_videos.extend(r.json().get("videos", []))

    if not all_videos:
        raise Exception("Keine Videos gefunden")

    # Duplikate entfernen
    seen_ids = set()
    unique_videos = []
    for v in all_videos:
        if str(v["id"]) not in seen_ids:
            seen_ids.add(str(v["id"]))
            unique_videos.append(v)

    print(f"📦 {len(unique_videos)} einzigartige Videos gefunden")

    # Cache filtern
    fresh_videos = [v for v in unique_videos if str(v["id"]) not in cache]
    if not fresh_videos:
        print("⚠️ Alle Videos schon genutzt – Cache wird geleert")
        cache = []
        fresh_videos = unique_videos

    # Passende Länge filtern
    suitable = [v for v in fresh_videos if v.get("duration", 0) >= duration]
    if not suitable:
        suitable = sorted(fresh_videos, key=lambda x: x.get("duration", 0), reverse=True)

    # Zufällig aus Top 10 wählen
    video = random.choice(suitable[:10])

    # Cache updaten
    cache.append(str(video["id"]))
    save_cache(cache)

    files = sorted(video["video_files"], key=lambda x: x.get("width", 0), reverse=True)
    video_url = files[0]["link"]
    print(f"⬇️ Lade Video (ID: {video['id']}, {video.get('duration')}s)...")
    resp = requests.get(video_url, stream=True)
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"✅ Hintergrundvideo: {output_path}")
    return output_path

def create_video(background_path, audio_path, output_path, duration):
    print("🎞️ Erstelle finales Video...")
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", background_path,
        "-i", audio_path,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,eq=brightness=-0.05:contrast=1.1",
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
        "-t", str(duration),
        "-movflags", "+faststart",
        "-pix_fmt", "yuv420p",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr[-3000:])
        raise Exception("FFmpeg fehlgeschlagen")
    size = Path(output_path).stat().st_size / (1024 * 1024)
    print(f"✅ Video: {output_path} ({size:.1f} MB)")
    return output_path

if __name__ == "__main__":
    today = datetime.now().strftime("%Y-%m-%d")
    from generate_voice import get_audio_duration
    duration = get_audio_duration(f"output/voice_{today}.mp3")
    download_background_video(f"output/background_{today}.mp4", duration)
    create_video(
        f"output/background_{today}.mp4",
        f"output/voice_{today}.mp3",
        f"output/final_{today}.mp4",
        duration
    )
