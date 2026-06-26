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
    "Starte mit einem konkreten schmerzhaften Moment — keine Einleitung, direkt mittendrin",
    "Beschreibe eine Situation die jeder kennt aber niemand ausspricht — so präzise dass es wehtut",
    "Sage eine brutale Wahrheit in einem Satz die sofort trifft",
    "Starte mit einer Handlung die Schmerz zeigt ohne das Wort Schmerz zu benutzen",
]

def get_heutiges_thema():
    kategorie = random.choice(list(THEMEN_KATEGORIEN.keys()))
    thema = random.choice(THEMEN_KATEGORIEN[kategorie])
    return kategorie, thema

def generate_text():
    client = anthropic.Anthropic()
    kategorie, thema = get_heutiges_thema()
    hook_typ = random.choice(HOOK_TYPEN)
    today = datetime.now().strftime("%Y-%m-%d")

    prompt = f"""Du bist Kopfgewitter — ein emotionaler deutscher TikTok-Account der Menschen trifft die zu viel fühlen und zu viel denken.

Schreibe einen kurzen viralen TikTok-Text zum Thema: "{thema}"

HOOK-PFLICHT — DIE ERSTE SEKUNDE ENTSCHEIDET:
Hook-Stil: {hook_typ}
Der allererste Satz muss so hart treffen dass man physisch aufhört zu scrollen.
VERBOTEN: "Das wusstest du...", "Wusstest du dass...", "Heute reden wir über..."
VERBOTEN: Lange Einleitungen — sofort ins Gefühl

STRUKTUR:
1. Hook (1-2 Sätze) — sofort der Schmerz, kein Warm-up
2. Aufbau (3-4 Sätze) — die Wunde vertiefen, Bilder die jeder kennt
3. Abschlusssatz — der hängen bleibt, kurz und brutal ehrlich
4. Ein CTA — Share-Trigger ODER Kommentar-Trigger, nie beides

BEISPIEL GUTER HOOK:
"Du schreibst. Gelesen. Keine Antwort."
"Dein Körper liegt still. Dein Kopf rennt Marathon."
"Du gibst alles. Und bekommst Krümel zurück."

REGELN:
- 55-70 Wörter (20-25 Sekunden)
- Max 6 Wörter pro Satz
- Immer "du/dich" — niemals "man"
- Jeder Satz eine eigene Zeile
- Kein Hashtag, kein "Folge Kopfgewitter"
- Jedes Wort muss sitzen — nichts ist zufällig

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
