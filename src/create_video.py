import os, subprocess, requests, random, json
from datetime import datetime
from pathlib import Path

PEXELS_API_KEY = os.environ["PEXELS_API_KEY"]
PIXABAY_API_KEY = os.environ["PIXABAY_API_KEY"]
CACHE_PATH = "used_videos.json"

VIDEO_TERMS = [
    "woman crying emotional",
    "person walking alone rain",
    "couple breaking up emotional",
    "woman looking window sad",
    "man emotional breakdown",
    "person sitting alone night",
    "emotional woman portrait",
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
        json.dump(cache[-100:], f, indent=2)

def fetch_pexels(term, duration):
    headers = {"Authorization": PEXELS_API_KEY}
    r = requests.get("https://api.pexels.com/videos/search", headers=headers,
        params={"query": term, "orientation": "portrait", "size": "medium", "per_page": 15})
    if r.status_code != 200:
        return []
    videos = []
    for v in r.json().get("videos", []):
        if v.get("duration", 0) >= duration:
            files = sorted(v["video_files"], key=lambda x: x.get("width", 0), reverse=True)
            videos.append({
                "id": f"pexels_{v['id']}",
                "url": files[0]["link"],
                "duration": v["duration"],
                "source": "pexels"
            })
    return videos

def fetch_pixabay(term, duration):
    r = requests.get("https://pixabay.com/api/videos/", params={
        "key": PIXABAY_API_KEY,
        "q": term,
        "video_type": "film",
        "per_page": 15,
        "safesearch": "true"
    })
    if r.status_code != 200:
        return []
    videos = []
    for v in r.json().get("hits", []):
        if v.get("duration", 0) >= duration:
            url = v["videos"]["medium"]["url"]
            if url:
                videos.append({
                    "id": f"pixabay_{v['id']}",
                    "url": url,
                    "duration": v["duration"],
                    "source": "pixabay"
                })
    return videos

def download_background_video(output_path, duration):
    cache = load_cache()
    all_videos = []

    terms = random.sample(VIDEO_TERMS, min(3, len(VIDEO_TERMS)))
    for term in terms:
        print(f"🎬 Suche Video: '{term}'")
        all_videos.extend(fetch_pexels(term, duration))
        all_videos.extend(fetch_pixabay(term, duration))

    if not all_videos:
        raise Exception("Keine Videos gefunden")

    # Duplikate entfernen
    seen_ids = set()
    unique_videos = []
    for v in all_videos:
        if v["id"] not in seen_ids:
            seen_ids.add(v["id"])
            unique_videos.append(v)

    print(f"📦 {len(unique_videos)} einzigartige Videos gefunden (Pexels + Pixabay)")

    # Cache filtern
    fresh_videos = [v for v in unique_videos if v["id"] not in cache]
    if not fresh_videos:
        print("⚠️ Cache geleert")
        cache = []
        fresh_videos = unique_videos

    # Zufällig aus Top 10 wählen
    video = random.choice(fresh_videos[:10])

    # Cache updaten
    cache.append(video["id"])
    save_cache(cache)

    print(f"⬇️ Lade Video ({video['source']}, {video['duration']}s)...")
    resp = requests.get(video["url"], stream=True)
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
