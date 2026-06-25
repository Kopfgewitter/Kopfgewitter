import os, subprocess, requests, random, math
from datetime import datetime
from pathlib import Path

PEXELS_API_KEY = os.environ["PEXELS_API_KEY"]

VIDEO_TERMS = [
    "woman crying emotional close up",
    "person walking alone rain",
    "couple breaking up emotional",
    "woman looking window sad",
    "man emotional breakdown crying",
    "person sitting alone night",
    "emotional woman portrait tears",
    "cinematic emotional people",
]

def download_video(url, output_path):
    resp = requests.get(url, stream=True)
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

def get_pexels_videos(count=4):
    headers = {"Authorization": PEXELS_API_KEY}
    videos = []
    terms_used = random.sample(VIDEO_TERMS, min(count, len(VIDEO_TERMS)))
    for term in terms_used:
        r = requests.get("https://api.pexels.com/videos/search", headers=headers,
            params={"query": term, "orientation": "portrait", "size": "medium", "per_page": 5})
        if r.status_code != 200:
            continue
        results = r.json().get("videos", [])
        if results:
            video = random.choice(results)
            files = sorted(video["video_files"], key=lambda x: x.get("width", 0), reverse=True)
            videos.append(files[0]["link"])
    return videos

def download_background_video(output_path, duration):
    print("🎬 Hole mehrere Hintergrundvideos...")
    clip_count = max(4, math.ceil(duration / 15))
    video_urls = get_pexels_videos(clip_count)
    if not video_urls:
        raise Exception("Keine Videos gefunden")
    clip_paths = []
    for i, url in enumerate(video_urls):
        path = output_path.replace(".mp4", f"_clip{i}.mp4")
        print(f"⬇️ Lade Clip {i+1}/{len(video_urls)}...")
        download_video(url, path)
        clip_paths.append(path)
    print("✂️ Schneide Clips zusammen...")
    concat_file = output_path.replace(".mp4", "_concat.txt")
    with open(concat_file, "w") as f:
        for path in clip_paths:
            f.write(f"file '{path}'\n")
cmd = [
    "ffmpeg", "-y",
    "-f", "concat", "-safe", "0", "-i", concat_file,
    "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
    "-c:v", "libx264", "-preset", "fast", "-crf", "23",
    "-an", "-t", str(duration + 5),
    output_path
]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("⚠️ Concat fehlgeschlagen, nutze erstes Video...")
        cmd2 = ["ffmpeg", "-y", "-stream_loop", "-1", "-i", clip_paths[0],
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-an",
            "-t", str(duration + 5), output_path]
        subprocess.run(cmd2, capture_output=True)
    for path in clip_paths:
        Path(path).unlink(missing_ok=True)
    Path(concat_file).unlink(missing_ok=True)
    print(f"✅ Hintergrundvideo: {output_path}")
    return output_path

def create_video(background_path, audio_path, output_path, duration):
    print("🎞️ Erstelle finales Video...")
    cmd = [
        "ffmpeg", "-y",
        "-i", background_path,
        "-i", audio_path,
        "-vf", "eq=brightness=-0.05:contrast=1.1",
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
