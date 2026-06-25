import anthropic, json, random
from datetime import datetime

TOPICS = [
    "jemanden verlieren der dich als selbstverständlich sah",
    "stilles Loslassen nach zu viel Schmerz",
    "Menschen die erst wertschätzen wenn es zu spät ist",
    "das Gefühl unsichtbar zu sein obwohl man alles gibt",
    "Overthinking und nicht abschalten können",
    "wenn man sich für jemanden verändert der es nicht verdient",
    "der Moment wo man aufhört zu kämpfen",
    "wenn Liebe einseitig wird",
    "sich selbst verlieren um jemand anderen glücklich zu machen",
    "die Einsamkeit mitten unter Menschen",
]

def generate_text():
    client = anthropic.Anthropic()
    topic = random.choice(TOPICS)
    today = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""Du bist ein emotionaler deutscher TikTok-Creator "Kopfgewitter".
Schreibe einen viralen TikTok-Text auf Deutsch zum Thema: "{topic}"
- Kurze kraftvolle Sätze (max 8 Wörter)
- Direkt mit "du/dich" ansprechen
- 120-180 Wörter (45-60 Sekunden)
- 1-2 Call-to-Actions mit 👉
- Beginne mit einem Hook der sofort trifft
Gib NUR den fertigen Text zurück."""
    msg = client.messages.create(model="claude-opus-4-6", max_tokens=1024,
        messages=[{"role": "user", "content": prompt}])
    text = msg.content[0].text.strip()
    result = {"date": today, "topic": topic, "text": text}
    with open(f"output/text_{today}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"✅ Text generiert | Thema: {topic}")
    print(text)
    return result

if __name__ == "__main__":
    generate_text()
