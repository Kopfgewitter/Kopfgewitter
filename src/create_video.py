import os, subprocess, requests, random, json
from datetime import datetime
from pathlib import Path

PEXELS_API_KEY = os.environ["PEXELS_API_KEY"]
CACHE_PATH = "output/used_videos.json"

PHOTO_TERMS = [
    "woman crying emotional",
    "person alone night window",
    "sad man sitting",
    "emotional portrait tears",
    "lonely person dark",
    "heartbreak couple distance",
    "person thinking night",
    "melancholic woman portrait",
    "person bedroom crying",
    "sad eyes closeup",
    "empty street night rain",
    "hands letting go",
]

def load_cache():
    if Path(CACHE_PATH).exists():
        with open(CACHE_PATH) as f:
            return json.load(f)
    return []

def save_cache(cache):
    Path("output").mkdir(exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(cache[-100:], f, indent=2)

def download_photos(output_dir, count):
    cache = load_cache()
    headers = {"Authorization": PEXELS_API_KEY}
    all_photos = []

    terms = random.sample(PHOTO_TERMS, min(4, len(PHOTO_TERMS)))
    for term in terms:
        print(f"🖼️ Suche Foto: '{term}'")
        r = requests.get("https://api.pexels.com/v1/search", headers=headers,
            params={"query": term, "orientation": "portrait", "per_page": 15})
        if r.status_code == 200:
            all_photos.extend(r.json().get("photos", []))

    # Duplikate entfernen
    seen_ids = set()
    unique_photos = []
    for p in all_photos:
        if str(p["id"]) not in seen_ids:
            seen_ids.add(str(p["id"]))
            unique_photos.append(p)

    print(f"📦 {len(unique_photos)} einzigartige Fotos gefunden")

    # Cache filtern
    fresh_photos = [p for p in unique_photos if str(p["id"]) not in cache]
    if not fresh_photos:
        print("⚠️ Cache geleert")
        cache = []
        fresh_photos = unique_photos

    # Zufällig auswählen
    selected = random.sample(fresh_photos[:30], min(count, len(fresh_photos[:30])))

    # Cache updaten
    for p in selected:
        cache.append(str(p["id"]))
    save_cache(cache)

    # Fotos herunterladen
    paths = []
    Path(output_dir).mkdir(exist_ok=True)
    for i, photo in enumerate(selected):
        url = photo["src"]["large"]
        path = f"{output_dir}/photo_{i:02d}.jpg"
        resp = requests.get(url, stream=True)
        with open(path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        paths.append(path)
        print(f"✅ Foto {i+1}/{len(selected)} gespeichert")

    return paths

def create_video(photo_dir, audio_path, output_path, duration):
    print("🎞️ Erstelle Slideshow...")

    # Fotos laden
    photo_paths = sorted(Path(photo_dir).glob("photo_*.jpg"))
    if not photo_paths:
        raise Exception("Keine Fotos gefunden")

    count = len(photo_paths)
    seconds_per_photo = duration / count
    print(f"📸 {count} Fotos, je {seconds_per_photo:.1f}s")

    # Concat filter für Slideshow bauen
    filter_parts = []
    for i in range(count):
        filter_parts.append(
            f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,"
            f"zoompan=z='min(zoom+0.0015,1.3)':d={int(seconds_per_photo*25)}:s=1080x1920,"
            f"eq=brightness=-0.05:contrast=1.1,"
            f"setsar=1,fps=25[v{i}]"
        )

    filter_str = ";".join(filter_parts)
    concat_inputs = "".join([f"[v{i}]" for i in range(count)])
    filter_str += f";{concat_inputs}concat=n={count}:v=1:a=0[outv]"

    # Input args für alle Fotos
    input_args = []
    for p in photo_paths:
        input_args += ["-loop", "1", "-t", str(seconds_per_photo), "-i", str(p)]

    cmd = [
        "ffmpeg", "-y",
        *input_args,
        "-i", audio_path,
        "-filter_complex", filter_str,
        "-map", "[outv]",
        "-map", f"{count}:a",
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
    print(f"✅ Slideshow: {output_path} ({size:.1f} MB)")
    return output_path

if __name__ == "__main__":
    today = datetime.now().strftime("%Y-%m-%d")
    from generate_voice import get_audio_duration
    duration = get_audio_duration(f"output/voice_{today}.mp3")
    count = max(5, int(duration / 4))
    photo_dir = f"output/photos_{today}"
    download_photos(photo_dir, count)
    create_video(
        photo_dir,
        f"output/voice_{today}.mp3",
        f"output/final_{today}.mp4",
        duration
    )
