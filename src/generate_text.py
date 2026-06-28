import anthropic, json, random
from datetime import datetime
from pathlib import Path

THEMEN_KATEGORIEN = {
    "einseitige_liebe": [
        "wenn du immer derjenige bist der schreibt",
        "wenn Liebe einseitig wird und du es zu spät merkst",
        "wenn du mehr gibst als du bekommst",
        "wenn du für jemanden kämpfst der dich nicht vermisst",
        "wenn deine Nachrichten auf gelesen bleiben",
        "wenn du weißt dass du zu viel bist für jemanden der zu wenig gibt",
        "wenn du hoffst dass sie sich ändern aber es nie passiert",
        "wenn du der einzige bist der noch an uns glaubt",
        "wenn Liebe sich anfühlt wie betteln",
        "wenn du liebst ohne geliebt zu werden",
        "wenn du bemerkst dass du ersetzt wurdest",
        "wenn jemand dich nur braucht wenn er einsam ist",
        "wenn du weißt dass du mehr verdienst aber nicht gehst",
    ],
    "verlust_und_loslassen": [
        "stilles Loslassen nach zu viel Schmerz",
        "wenn man jemanden verliert der einen als selbstverständlich sah",
        "der Moment wo man aufhört zu kämpfen",
        "wenn du jemanden liebst aber loslassen musst",
        "wenn eine Beziehung stirbt bevor sie endet",
        "wenn loslassen sich schlimmer anfühlt als bleiben",
        "wenn du jemanden vermisst der noch lebt",
        "wenn du weißt es ist vorbei aber dein Herz es nicht akzeptiert",
        "wenn du Erinnerungen löschst um weiterzumachen",
        "wenn das letzte Gespräch nicht so war wie du es wolltest",
        "wenn du nicht weißt ob du trauern sollst weil nichts offiziell war",
        "wenn jemand geht ohne zu erklären warum",
        "wenn du aufhörst zu warten und es sich wie Verrat anfühlt",
    ],
    "modernes_dating": [
        "wenn jemand dich ghostet nach allem was ihr geteilt habt",
        "wenn Gefühle per Nachricht beendet werden",
        "wenn jemand dich auf Abstand hält aber nicht loslässt",
        "wenn man nicht zusammen ist aber auch nicht getrennt",
        "wenn Social Media zeigt dass er ohne dich weitermacht",
        "wenn jemand sagt er braucht Zeit aber postet täglich Stories",
        "wenn du nicht weißt was ihr seid",
        "wenn jemand dich behandelt als wärst du eine Option",
        "wenn du auf eine Antwort wartest die nie kommt",
        "wenn jemand dich nur nachts braucht",
        "wenn Emojis mehr sagen als echte Worte",
        "wenn jemand dich daten will aber keine Beziehung",
        "wenn du nicht weißt ob du zu viel erwartest",
        "wenn jemand perfekt klingt aber nie da ist",
    ],
    "selbstverlust": [
        "wenn man sich für jemanden verändert der es nicht verdient",
        "sich selbst verlieren um jemand anderen glücklich zu machen",
        "wenn du nicht mehr weißt wer du ohne diese Person bist",
        "wenn du deine eigenen Bedürfnisse ignorierst für andere",
        "wenn du dich klein machst damit jemand anderes groß wirkt",
        "wenn du dich selbst nicht mehr erkennst",
        "wenn du merkst dass du dich verändert hast um zu gefallen",
        "wenn du deine Träume aufgibst für jemand anderen",
        "wenn du dich entschuldigst für Dinge die keine Entschuldigung verdienen",
        "wenn andere bestimmen wer du sein sollst",
        "wenn du vergisst was du dir selbst versprochen hast",
        "wenn du dich selbst am wenigsten liebst",
    ],
    "einsamkeit_und_overthinking": [
        "die Einsamkeit mitten unter Menschen",
        "Overthinking und nicht abschalten können",
        "wenn du nachts nicht schlafen kannst wegen Gedanken",
        "wenn du lächelst aber innerlich weinst",
        "wenn du das Gefühl hast niemand versteht dich wirklich",
        "wenn du Gespräche im Kopf führst die nie stattfinden",
        "wenn du um 3 Uhr nachts allein mit deinen Gedanken bist",
        "wenn du alles analysierst bis es keinen Sinn mehr macht",
        "wenn du Worte bereust die du gesagt oder nicht gesagt hast",
        "wenn du dir vorstellst wie es wäre wenn alles anders wäre",
        "wenn du Angst hast zu fühlen weil Fühlen wehtut",
        "wenn du nicht weißt warum du traurig bist aber es trotzdem bist",
        "wenn du funktionierst aber nicht lebst",
        "wenn du Menschen brauchst aber Nähe Angst macht",
    ],
    "unsichtbarkeit": [
        "das Gefühl unsichtbar zu sein obwohl man alles gibt",
        "wenn Menschen dich erst wertschätzen wenn es zu spät ist",
        "wenn du der Einzige bist der sich Mühe gibt",
        "wenn dein Schmerz von niemandem gesehen wird",
        "wenn du für alle da bist aber niemand für dich",
        "wenn du redest aber niemand zuhört",
        "wenn du fehlst aber niemand fragt wo du bist",
        "wenn du hilfst aber niemand fragt wie es dir geht",
        "wenn du stark sein musst weil niemand deine Schwäche aushält",
        "wenn du merkst dass du ersetzbar bist",
        "wenn du dich anstrengst aber es nicht gesehen wird",
        "wenn du weinst aber alleine damit bist",
    ],
    "toxische_muster": [
        "wenn jemand dich immer wieder zurückzieht und dann loslässt",
        "wenn Entschuldigungen nichts ändern",
        "wenn du weißt dass es falsch ist aber trotzdem bleibst",
        "wenn Hoffnung dich in einer schlechten Situation hält",
        "wenn jemand dich liebt aber trotzdem verletzt",
        "wenn du immer wieder verzeihst obwohl du es nicht solltest",
        "wenn jemand sagt er liebt dich aber es sich nicht so anfühlt",
        "wenn du Ausreden für jemandes Verhalten erfindest",
        "wenn du weißt wie es endet aber trotzdem anfängst",
        "wenn du dich für jemandes schlechtes Verhalten verantwortlich fühlst",
        "wenn du glückliche Momente festhalten willst weil du weißt sie vergehen",
        "wenn du immer wieder zurückgehst egal was passiert ist",
    ],
    "heilung_und_wahrheit": [
        "wenn du merkst dass du dich selbst vernachlässigt hast",
        "der Moment wo du aufhörst um Liebe zu betteln",
        "wenn du verstehst dass nicht alle bleiben sollen",
        "wenn Schmerz dich stärker macht als du wolltest",
        "wenn du lernst dass Einsamkeit besser ist als falsche Gesellschaft",
        "wenn du aufhörst zu erklären wer du bist",
        "wenn du merkst dass du ohne ihn funktionierst",
        "wenn du dir selbst gibst was du anderen gegeben hast",
        "wenn Loslassen sich wie Befreiung anfühlt",
        "wenn du aufhörst jemanden zu suchen der nicht gesucht werden will",
        "wenn du lernst nein zu sagen ohne dich zu erklären",
        "wenn du merkst dass du genug bist",
    ],
}

HOOK_TYPEN = [
    "Ein einziger Satz — so präzise dass der Zuschauer denkt du beschreibst sein Leben",
    "Zeige eine Alltagshandlung die Schmerz ausdrückt — kein einziges emotionales Wort benutzen",
    "Zwei Sätze die sich widersprechen — ein Gegensatz der sofort unter die Haut geht",
    "Die eine Wahrheit die alle kennen aber niemand laut ausspricht — brutal kurz und direkt",
    "Starte mitten in einem Moment — kein Kontext, keine Erklärung, sofort der Schmerz",
]

CTAS = [
    "Schick das der Person die das gerade durchmacht. 💔",
    "Markier die Person die das kennt.",
    "Schick das jemandem der das nie sagen würde aber fühlt. 💔",
    "Markier die Person die du gerade vermisst.",
    "Schick das der Person die immer für alle da ist. 💔",
    "Schreib 💔 wenn du weißt wie sich das anfühlt.",
    "Kommentier 🖤 wenn dich das gerade trifft.",
    "Schick das der Person die du nie vergessen konntest.",
]

FOLLOW_TRIGGER = [
    "Folge uns — für alle die zu viel fühlen.",
    "Kopfgewitter — wir sagen was du fühlst.",
    "Folge uns wenn dich das getroffen hat.",
    "Kopfgewitter — für die die nachts nicht schlafen können.",
    "Folge uns. Hier wirst du verstanden. 🖤",
]

def get_heutiges_thema():
    kategorie = random.choice(list(THEMEN_KATEGORIEN.keys()))
    thema = random.choice(THEMEN_KATEGORIEN[kategorie])
    return kategorie, thema

def generate_text():
    client = anthropic.Anthropic()
    kategorie, thema = get_heutiges_thema()
    hook_typ = random.choice(HOOK_TYPEN)
    cta = random.choice(CTAS)
    follow_trigger = random.choice(FOLLOW_TRIGGER)
    today = datetime.now().strftime("%Y-%m-%d")

    prompt = f"""Du bist Kopfgewitter — der emotionalste deutsche TikTok-Account für Menschen die zu viel fühlen und zu viel denken.

Thema: "{thema}"

HOOK — ERSTE SEKUNDE ENTSCHEIDET ALLES:
Stil: {hook_typ}
Der erste Satz muss so hart treffen dass der Finger aufhört zu scrollen.
VERBOTEN: "Das wusstest du..." / "Wusstest du dass..." / lange Einleitungen / erklärende Sätze
PFLICHT: Sofort mitten im Schmerz — null Warm-up

ERFOLGREICHE HOOK-BEISPIELE VON TOP ACCOUNTS:
"dein verhalten hat alles kaputt gemacht."
"Du warst nicht die Eine. Du warst die Pause zwischen zwei Kapiteln."
"Du schreibst. Gelesen. Keine Antwort."
"Du gibst Ozean. Und bekommst Pfützen zurück."
"3 Uhr nachts. Alle schlafen. Nur du nicht."
"Er liebt dich nicht. 💔"

STRUKTUR:
1. Hook (1 Satz) — sofort der härteste Moment, null Kontext
2. Aufbau (3-4 Sätze) — konkrete Alltagsbilder die jeder kennt, Wunde vertiefen
3. Wendepunkt (1 Satz) — die brutalste Wahrheit oder die Erkenntnis die wehtut
4. CTA: "{cta}"
5. Follow: "{follow_trigger}"

POLARISIERUNGS-REGELN:
- Jeder Satz löst eine eigene Emotion aus
- Kein Satz darf austauschbar sein
- Beim zweiten Lesen trifft es noch härter
- Konkret schreiben — niemals abstrakt
- 1-2 Emojis erlaubt — nur 💔 oder 🖤, nie mehr

TECHNISCHE REGELN:
- 55-70 Wörter gesamt
- Max 6 Wörter pro Satz
- Nur "du/dich" — niemals "man"
- Jeder Satz eine eigene Zeile
- Kein Hashtag

Gib NUR den fertigen Text zurück."""

    msg = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )
    text = msg.content[0].text.strip()
    result = {"date": today, "kategorie": kategorie, "topic": thema, "text": text}
    with open(f"output/text_{today}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"✅ Text generiert | Kategorie: {kategorie} | Thema: {thema}")
    print(text)
    return result

if __name__ == "__main__":
    generate_text()
