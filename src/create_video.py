import os, subprocess, requests, random, json
from datetime import datetime
from pathlib import Path

PEXELS_API_KEY = os.environ["PEXELS_API_KEY"]
PIXABAY_API_KEY = os.environ["PIXABAY_API_KEY"]
CACHE_PATH = "used_videos.json"

VIDEO_TERMS = {
    "herzschmerz": [
        "couple breaking up emotional", "heartbreak sad woman", "crying woman bedroom",
        "emotional breakup scene", "woman tears night", "broken heart sad person"
    ],
    "einsamkeit": [
        "person sitting alone night", "lonely person dark room", "woman looking window sad",
        "man alone city night", "empty room lonely", "person alone bench night"
    ],
    "sehnsucht": [
        "woman thinking night window", "melancholic woman portrait", "person staring distance",
        "sad woman rain window", "longing emotional woman", "dreaming person night"
    ],
    "gedanken": [
        "person overthinking stress", "woman emotional breakdown", "man emotional breakdown",
        "cinematic emotional people", "person head hands stressed", "thinking person dark"
    ],
    "trauer": [
        "person crying emotional", "woman crying emotional", "sad man sitting alone",
        "emotional couple distance", "person crying rain", "grief emotional scene"
    ],
}

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

    category = random.choice(list(VIDEO_TERMS.keys()))
    terms = random.sample(VIDEO_TERMS[category], min(3, len(VIDEO_TERMS[category])))

    for term in terms:
        print(f"🎬 Suche Video [{category}]: '{term}'")
        all_videos.extend(fetch_pexels(term, duration))
        all_videos.extend(fetch_pixabay(term, duration))

    if not all_videos:
        raise Exception("Keine Videos gefunden")

    seen_ids = set()
    unique_videos = []
    for v in all_videos:
        if v["id"] not in seen_ids:
            seen_ids.add(v["id"])
            unique_videos.append(v)

    print(f"📦 {len(unique_videos)} einzigartige Videos gefunden (Pexels + Pixabay)")

    fresh_videos = [v for v in unique_videos if v["id"] not in cache]
    if not fresh_videos:
        print("⚠️ Cache geleert")
        cache = []
        fresh_videos = unique_videos

    video = random.choice(fresh_videos[:10])
    cache.append(video["id"])
    save_cache(cache)

    print(f"⬇️ Lade Video ({video['source']}, {video['duration']}s)...")
    resp = requests.get(video["url"], stream=True)
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"✅ Hintergrundvideo: {output_path}")
    return output_path

def clean_text_for_ffmpeg(text):
    """Entfernt alle Emojis und Sonderzeichen die FFmpeg nicht verarbeiten kann."""
    text = text.replace("💔", "").replace("🖤", "").replace("❤️", "")
    text = text.replace("\u200d", "").replace("\ufe0f", "").replace("\u2764", "")
    text = text.replace("'", "\\'").replace(":", "\\:").replace(",", "\\,")
    text = text.strip()
    return text

def build_visual_hook(hook_text, hook_duration=4.0):
    """Erster Satz groß oben im Bild – bleibt 4 Sekunden sichtbar.
    Untertitel laufen gleichzeitig unten normal weiter."""
    safe = clean_text_for_ffmpeg(hook_text)

    words = safe.split()
    if len(words) > 5:
        mid = len(words) // 2
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:])
        text_filter = (
            f"drawtext=text='{line1}'"
            f":fontsize=76"
            f":fontcolor=white"
            f":font='Liberation Sans'"
            f":borderw=6"
            f":bordercolor=black"
            f":x=(w-text_w)/2"
            f":y=(h*0.18)"
            f":enable='between(t,0,{hook_duration})',"
            f"drawtext=text='{line2}'"
            f":fontsize=76"
            f":fontcolor=white"
            f":font='Liberation Sans'"
            f":borderw=6"
            f":bordercolor=black"
            f":x=(w-text_w)/2"
            f":y=(h*0.18)+90"
            f":enable='between(t,0,{hook_duration})'"
        )
    else:
        text_filter = (
            f"drawtext=text='{safe}'"
            f":fontsize=82"
            f":fontcolor=white"
            f":font='Liberation Sans'"
            f":borderw=6"
            f":bordercolor=black"
            f":x=(w-text_w)/2"
            f":y=(h*0.18)"
            f":enable='between(t,0,{hook_duration})'"
        )

    overlay = (
        f"drawbox=x=0:y=(h*0.12):w=iw:h=220"
        f":color=black@0.5:t=fill"
        f":enable='between(t,0,{hook_duration})'"
    )

    return overlay + "," + text_filter

def build_subtitle_filter(timestamps, total_duration, fontsize=52):
    """Untertitel laufen unten – gleichzeitig mit dem visuellen Hook."""
    filters = []
    for i, entry in enumerate(timestamps):
        text = entry["text"]
        start = entry.get("start")
        if start is None:
            start = (i / len(timestamps)) * total_duration

        if i + 1 < len(timestamps):
            next_start = timestamps[i + 1].get("start")
            if next_start is None:
                next_start = ((i + 1) / len(timestamps)) * total_duration
            end = next_start
        else:
            end = total_duration

        safe_text = clean_text_for_ffmpeg(text)

        if len(safe_text) > 30:
            words = safe_text.split()
            mid = len(words) // 2
            safe_text = " ".join(words[:mid]) + "\n" + " ".join(words[mid:])

        filter_str = (
            f"drawtext=text='{safe_text}'"
            f":fontsize={fontsize}"
            f":fontcolor=white"
            f":font='Liberation Sans'"
            f":borderw=3"
            f":bordercolor=black"
            f":x=(w-text_w)/2"
            f":y=(h*0.75)-text_h/2"
            f":enable='between(t,{start},{end})'"
        )
        filters.append(filter_str)
    return ",".join(filters)

def create_thumbnail(video_path, output_path, hook_text):
    print("🖼️ Erstelle Thumbnail...")

    frame_path = output_path.replace(".jpg", "_frame.jpg")
    cmd_frame = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vframes", "1",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-q:v", "2",
        frame_path
    ]
    subprocess.run(cmd_frame, capture_output=True)

    lines = [l.strip() for l in hook_text.split("\n") if l.strip()]
    hook_line = lines[0] if lines else "Kopfgewitter"

    words = hook_line.split()
    if len(words) > 4:
        mid = len(words) // 2
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:])
    else:
        line1 = hook_line
        line2 = ""

    def escape(t):
        t = t.replace("💔", "").replace("🖤", "").replace("❤️", "")
        t = t.replace("\u200d", "").replace("\ufe0f", "").replace("\u2764", "")
        t = t.replace("'", "\\'").replace(":", "\\:").replace(",", "\\,")
        return t.strip()

    drawtext_filters = []

    drawtext_filters.append(
        "drawbox=x=0:y=0:w=iw:h=ih:color=black@0.45:t=fill"
    )

    drawtext_filters.append(
        f"drawtext=text='kopfgewitter'"
        f":fontsize=42"
        f":fontcolor=white@0.6"
        f":font='Liberation Sans'"
        f":x=(w-text_w)/2"
        f":y=100"
    )

    drawtext_filters.append(
        f"drawtext=text='{escape(line1)}'"
        f":fontsize=82"
        f":fontcolor=white"
        f":font='Liberation Sans'"
        f":borderw=5"
        f":bordercolor=black"
        f":x=(w-text_w)/2"
        f":y=(h/2)-100"
    )

    if line2:
        drawtext_filters.append(
            f"drawtext=text='{escape(line2)}'"
            f":fontsize=82"
            f":fontcolor=white"
            f":font='Liberation Sans'"
            f":borderw=5"
            f":bordercolor=black"
            f":x=(w-text_w)/2"
            f":y=(h/2)+10"
        )

    vf = ",".join(drawtext_filters)

    cmd_thumb = [
        "ffmpeg", "-y",
        "-i", frame_path,
        "-vf", vf,
        "-q:v", "2",
        output_path
    ]

    result = subprocess.run(cmd_thumb, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"⚠️ Thumbnail Fehler: {result.stderr[-500:]}")
        return None

    Path(frame_path).unlink(missing_ok=True)
    print(f"✅ Thumbnail: {output_path}")
    return output_path

def create_video(background_path, audio_path, output_path, duration, timestamps_path=None, text_data=None):
    print("🎞️ Erstelle finales Video...")

    timestamps = []
    if timestamps_path and Path(timestamps_path).exists():
        with open(timestamps_path, encoding="utf-8") as f:
            timestamps = json.load(f)
        print(f"✅ {len(timestamps)} Satz-Timestamps geladen")

    vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,eq=brightness=-0.05:contrast=1.1"

    hook_duration = 4.0
    if timestamps and len(timestamps) > 0:
        hook_text = timestamps[0]["text"]
        hook_filter = build_visual_hook(hook_text, hook_duration)
        vf += "," + hook_filter
        print(f"✅ Visueller Hook ({hook_duration}s): '{hook_text[:40]}'")

    if timestamps:
        subtitle_filter = build_subtitle_filter(timestamps, duration)
        vf += "," + subtitle_filter
        print("✅ Synchrone Untertitel eingebaut")
    else:
        print("⚠️ Keine Timestamps — kein Untertitel")

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", background_path,
        "-i", audio_path,
        "-vf", vf,
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

    if text_data:
        thumb_path = output_path.replace(".mp4", "_thumb.jpg")
        create_thumbnail(output_path, thumb_path, text_data.get("text", ""))

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
        duration,
        timestamps_path=f"output/voice_{today}_timestamps.json"
    )
