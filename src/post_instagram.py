import os, json, requests, time
from datetime import datetime
from pathlib import Path

INSTAGRAM_ACCESS_TOKEN = os.environ["INSTAGRAM_ACCESS_TOKEN"]
INSTAGRAM_ACCOUNT_ID = os.environ["INSTAGRAM_ACCOUNT_ID"]

def post_to_instagram(video_path, caption):
    print("📤 Instagram Upload...")

    # Schritt 1: Container erstellen
    container_url = f"https://graph.instagram.com/v21.0/{INSTAGRAM_ACCOUNT_ID}/media"
    container_r = requests.post(container_url, data={
        "media_type": "REELS",
        "video_url": video_path,
        "caption": caption,
        "share_to_feed": "true",
        "access_token": INSTAGRAM_ACCESS_TOKEN
    })

    if container_r.status_code != 200:
        raise Exception(f"Instagram Container Fehler {container_r.status_code}: {container_r.text}")

    container_id = container_r.json().get("id")
    print(f"✅ Container erstellt (ID: {container_id})")

    # Schritt 2: Warten bis Video verarbeitet
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

    # Schritt 3: Veröffentlichen
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

if __name__ == "__main__":
    today = datetime.now().strftime("%Y-%m-%d")
    with open(f"output/text_{today}.json", encoding="utf-8") as f:
        data = json.load(f)
    from post_tiktok import generate_caption
    caption = generate_caption(data)
    result = post_to_instagram(f"output/final_{today}.mp4", caption)
    print(result)
