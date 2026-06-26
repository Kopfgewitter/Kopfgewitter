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
    "wenn du merkst dass du nicht mehr wichtig bist",
    "der Schmerz den niemand sieht",
    "wenn Schweigen mehr sagt als Worte",
    "Menschen die bleiben wenn es schwer wird",
    "das Gefühl morgens aufzuwachen und nichts zu fühlen",
]

HOOK_TYPEN = [
    "Direkt ins Gefühl — keine Ankündigung, sofort der schmerzhafte Moment",
    "Eine Situation beschreiben die jeder kennt aber niemand ausspricht",
    "Eine Frage die sofort trifft und zum Nachdenken zwingt",
    "Eine brutale Wahrheit die wehtut aber befreit",
]

def generate_text():
    client = anthropic.Anthropic()
    topic = random.choice(TOPICS)
    hook_typ = random.choice(HOOK_TYPEN)
    today = datetime.now().strftime("%Y-%m-%d")

    prompt = f"""Du bist Kopfgewitter — ein emotionaler deutscher TikTok-Account der Menschen trifft die zu viel fühlen und zu viel denken.

Schreibe einen viralen TikTok-Text zum Thema: "{topic}"

HOOK-REGEL (die ersten 2 Sätze entscheiden alles):
Hook-Stil: {hook_typ}
NIEMALS mit "Das wusstest du..." oder "Wusstest du dass..." beginnen — das ist abgenutzt.
Der erste Satz muss so treffen dass man nicht weiterscrollen kann.

STRUKTUR:
1. Hook (2 Sätze) — sofort mitten ins Gefühl
2. Aufbau (5-8 Sätze) — die Situation vertiefen, Bilder erzeugen
3. Wendepunkt (2-3 Sätze) — die Erkenntnis oder der Schmerz der bleibt
4. Abschluss mit 2 CTAs:
   - Einen Share-Trigger: "Schick das jemandem der..." oder "Zeig das der Person die..."
   - Einen Kommentar-Trigger: "Schreib 🖤 wenn du weißt wie sich das anfühlt"

REGELN:
- Kurze kraftvolle Sätze (max 8 Wörter pro Satz)
- Immer "du/dich" — direkte Ansprache
- 130-160 Wörter (45-55 Sekunden)
- Kein Hashtag im Text
- Kein "Folge Kopfgewitter" — wirkt billig
- Jeder Satz muss eine eigene Zeile sein

Gib NUR den fertigen Text zurück, nichts anderes."""

    msg = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    text = msg.content[0].text.strip()
    result = {"date": today, "topic": topic, "text": text}
    with open(f"output/text_{today}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"✅ Text generiert | Thema: {topic}")
    print(text)
    return result

if __name__ == "__main__":
    generate_text()
