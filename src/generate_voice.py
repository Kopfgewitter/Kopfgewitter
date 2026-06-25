import os, json, requests, subprocess
from datetime import datetime
from pathlib import Path

ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]
VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "onwK4e9ZLuTAKqWW03F9")

def generate_voice(text, output_path):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
    payload = {"text": text, "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.30, "similarity_boost": 0.85, "style": 0.75, "use_speaker_boost": True}}
    print("🎙️ Generiere Voiceover...")
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code != 200:
        raise Exception(f"ElevenLabs Fehler {r.status_code}: {r.text}")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(r.content)
    print(f"✅ Voiceover: {output_path}")
    return output_path

def get_audio_duration(audio_path):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", audio_path], capture_output=True, text=True)
    return float(result.stdout.strip())

if __name__ == "__main__":
    today = datetime.now().strftime("%Y-%m-%d")
    with open(f"output/text_{today}.json", encoding="utf-8") as f:
        data = json.load(f)
    generate_voice(data["text"], f"output/voice_{today}.mp3")
