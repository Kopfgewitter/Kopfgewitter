import os, json, requests, time
import cloudinary
import cloudinary.uploader
from datetime import datetime
from pathlib import Path

INSTAGRAM_ACCESS_TOKEN = os.environ["INSTAGRAM_ACCESS_TOKEN"]
INSTAGRAM_ACCOUNT_ID = os.environ["INSTAGRAM_ACCOUNT_ID"]

cloudinary.config(
    cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
    api_key=os.environ["CLOUDINARY_API_KEY"],
    api_secret=os.environ["CLOUDINARY_API_SECRET"]
)

def upload_to_cloudinary(video_path):
    print("☁️ Lade Video zu Cloudinary hoch...")
    result = cloudinary.uploader.upload(
        video_path,
        resource_type="video",
        folder="kopfgewitter",
    )
    url = result.get("secure_url")
    print(f"✅ Cloudinary URL: {url}")
    return url

def post_to_instagram(video_path, caption, video_url=None):
    print("📤 Instagram Upload...")

    if not video_url:
        video_url = upload_to_cloudinary(video_path)

    container_url = f"https://graph.instagram.com/v21.0/{INSTAGRAM_ACCOUNT_ID}/media"
    container_r = requests.post(container_url, data={
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "share_to_feed": "true",
        "access_token": INSTAGRAM_ACCESS_TOKEN
    })

    if container_r.status_code != 200:
        raise Exception(f"Instagram Container Fehler {container_r.status_code}: {container_r.text}")

    container_id = container_r.json().get("id")
    print(f"✅ Container erstellt (ID: {container_id})")

    print("⏳ Warte auf Verarbeitung...")
    for attempt in range(20):
        time.sleep(10)
        status_url = f"https://graph.instagram.com/v21.0/{container_id}"
        status_r = requests.get(status_url, params={
            "fields": "status_code",
            "access_token": INSTAGRAM_ACCESS_TOKEN
        })
        if status_r.status_code == 200:
            status = status_r.json().get("status_code", "")
            print(f"  Status: {status} (Versuch {attempt+1}/20)")
            if status == "FINISHED":
                break
            elif status == "ERROR":
                raise Exception("Instagram Verarbeitungsfehler")

    publish_url = f"https://graph.instagram.com/v21.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
    publish_r = requests.post(publish_url, data={
        "creation_id": container_id,
        "access_token": INSTAGRAM_ACCESS_TOKEN
    })

    if publish_r.status_code != 200:
        raise Exception(f"Instagram Publish Fehler {publish_r.status_code}: {publish_r.text}")

    media_id = publish_r.json().get("id")
    print(f"🎉 Erfolgreich auf Instagram veröffentlicht! (ID: {media_id})")
    return {"success": True, "media_id": media_id}
