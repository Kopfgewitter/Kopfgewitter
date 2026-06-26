import os, json, requests, time
from datetime import datetime
from pathlib import Path

TIKTOK_ACCESS_TOKEN = os.environ["TIKTOK_ACCESS_TOKEN"]

KATEGORIE_HASHTAGS = {
    "einseitige_liebe":        "#liebeskummer #herzschmerz #beziehung #gedankenwelt #kopfgewitter",
    "verlust_und_loslassen":   "#loslassen #herzschmerz #liebeskummer #wahreworte #kopfgewitter",
    "modernes_dating":         "#liebeskummer #dating #beziehung #herzschmerz #kopfgewitter",
    "selbstverlust":           "#selbstliebe #gedanken #wahreworte #beziehung #kopfgewitter",
    "einsamkeit_und_overthinking": "#gedankenkarussell #einsamkeit #gedanken #wahreworte #kopfgewitter",
    "unsichtbarkeit":          "#einsamkeit #herzschmerz #gedankenwelt #wahreworte #kopfgewitter",
    "toxische_muster":         "#toxisch #liebeskummer #herzschmerz #beziehung #kopfgewitter",
    "heilung_und_wahrheit":    "#selbstliebe #loslassen #wahreworte #gedanken #kopfgewitter",
}

def generate_caption(text_data):
    text = text_data["text"]
    kategorie = text_data.get("kategorie", "")
    hashtags = KATEGORIE_HASHTAGS.get(kategorie, "#herzschmerz #gefühle #gedanken #wahreworte #kopfgewitter")
    caption = f"{text}\n\n{hashtags}"
    return caption[:2200]

def post_to_tiktok(video_path, caption):
    video_size = Path(video_path).stat().st_size
    print(f"📤 TikTok Upload ({video_size/1024/1024:.1f} MB)...")
    headers = {"Authorization": f"Bearer {TIKTOK_ACCESS_TOKEN}", "Content-Type": "application/json"}
    init_r = requests.post("https://open.tiktokapis.com/v2/post/publish/video/init/", headers=headers,
        json={"post_info": {"title": caption, "privacy_level": "PUBLIC_TO_EVERYONE",
            "disable_duet": False, "disable_comment": False, "disable_stitch": False},
            "source_info": {"source": "FILE_UPLOAD", "video_size": video_size,
                "chunk_size": video_size, "total_chunk_count": 1}})
    if init_r.status_code != 200:
        raise Exception(f"TikTok Init Fehler {init_r.status_code}: {init_r.text}")
    init_data = init_r.json()
    publish_id = init_data["data"]["publish_id"]
    upload_url = init_data["data"]["upload_url"]
    print(f"✅ Upload initialisiert (ID: {publish_id})")
    with open(video_path, "rb") as f:
        video_data = f.read()
    upload_r = requests.put(upload_url,
        headers={"Content-Type": "video/mp4", "Content-Range": f"bytes 0-{video_size-1}/{video_size}",
            "Content-Length": str(video_size)}, data=video_data)
    if upload_r.status_code not in [200, 201, 206]:
        raise Exception(f"Upload Fehler {upload_r.status_code}")
    print("✅ Video hochgeladen!")
    for attempt in range(20):
        time.sleep(5)
        status_r = requests.post("https://open.tiktokapis.com/v2/post/publish/status/fetch/",
            headers=headers, json={"publish_id": publish_id})
        if status_r.status_code == 200:
            status = status_r.json().get("data", {}).get("status", "")
            print(f"  Status: {status} (Versuch {attempt+1}/20)")
            if status == "PUBLISH_COMPLETE":
                print("🎉 Erfolgreich auf TikTok veröffentlicht!")
                return {"success": True, "publish_id": publish_id, "status": status}
            elif status in ["FAILED", "CANCELLED"]:
                raise Exception(f"Fehlgeschlagen: {status}")
    return {"success": True, "publish_id": publish_id, "status": "PENDING"}

if __name__ == "__main__":
    today = datetime.now().strftime("%Y-%m-%d")
    with open(f"output/text_{today}.json", encoding="utf-8") as f:
        data = json.load(f)
    caption = generate_caption(data)
    result = post_to_tiktok(f"output/final_{today}.mp4", caption)
    print(result)
