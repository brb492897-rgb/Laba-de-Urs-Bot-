import os
import random
import requests

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

GEMINI_MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """
Ești Laba de Urs 🐻, un bot de Telegram pentru un grup de prieteni.

PERSONALITATE:
- Ești foarte sociabil.
- Ești amuzant și faci caterincă.
- Vorbești natural, în română.
- Poți folosi limbaj colocvial și vulgar moderat când se potrivește
  contextului de glumă.
- Nu trebuie să fii politicos excesiv.
- Răspunsurile sunt de obicei scurte și amuzante.
- Nu răspunde robotic.
- Nu repeta aceeași glumă mereu.

IMPORTANT:
Nu răspunde la absolut fiecare mesaj banal.
Dacă mesajul nu necesită răspuns, răspunde cu exact:
SKIP

Dacă cineva te salută sau îți vorbește direct, răspunde.

Dacă cineva înjură, poți răspunde în stil de caterincă, de exemplu:
„Taci, bă, că te ia Laba de Urs 😂🐻”

Nu amenința serios și nu încuraja violența reală.
Totul trebuie să fie clar în spirit de glumă.

Nu pretinde că ești om.
Dacă cineva întreabă cine ești, spune că ești botul Laba de Urs.
"""

CUVINTE_INJURATURI = [
    "muie",
    "pula",
    "pulă",
    "coaie",
    "coaiele",
    "fut",
    "futu",
    "futut",
    "căcat",
    "cacat",
    "cur",
    "curva",
    "curvă",
    "idiot",
    "prost"
]

REPLICI_CATERINCA = [
    "Taci, bă, că te-a auzit ursul 😂🐻",
    "Bă, ușor cu vocabularul, că se sperie ursul 😂🐻",
    "Gata, mă, iar ai pornit motorul de înjurături? 😂",
    "Băăă, ce limbaj ai azi 😂🐻",
    "Mai încet, campionule, că te vede Laba de Urs 😂",
    "Ce-ai băut azi de ai venit cu asemenea vocabular? 😂🐻"
]


def contine_injuratura(text):
    text = text.lower()

    for cuvant in CUVINTE_INJURATURI:
        if cuvant in text:
            return True

    return False


def gemini_response(text):
    if not GEMINI_API_KEY:
        return "❌ GEMINI_API_KEY nu este setat în Railway."

    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{GEMINI_MODEL}:generateContent"
    )

    headers = {
        "x-goog-api-key": GEMINI_API_KEY.strip(),
        "Content-Type": "application/json"
    }

    payload = {
        "system_instruction": {
            "parts": [
                {
                    "text": SYSTEM_PROMPT
                }
            ]
        },
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": text
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 1.0,
            "maxOutputTokens": 180
        }
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        data = response.json()

        if response.status_code != 200:
            error = data.get("error", {})
            return (
                "❌ Gemini: "
                + error.get("message", "eroare necunoscută")
            )

        candidates = data.get("candidates", [])

        if not candidates:
            return "SKIP"

        parts = candidates[0].get(
            "content", {}
        ).get("parts", [])

        if not parts:
            return "SKIP"

        return parts[0].get(
            "text", ""
        ).strip()

    except Exception as e:
        print("Gemini error:", e)
        return "❌ Eroare Gemini."


async def mesaj_primit(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    text = update.message.text

    if not text:
        return

    # Dacă înjură, răspunde imediat cu caterincă
    if contine_injuratura(text):
        await update.message.reply_text(
            random.choice(REPLICI_CATERINCA)
        )
        return

    # Altfel lasă Gemini să decidă dacă răspunde
    answer = gemini_response(text)

    if not answer or answer == "SKIP":
        return

    await update.message.reply_text(answer)


def main():

    if not TOKEN:
        print("❌ BOT_TOKEN lipsește!")
        return

    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY lipsește!")
        return

    print("🐻 LABA DE URS PORNITĂ!")
    print("🤖 AI: Gemini")

    app = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            mesaj_primit
        )
    )

    app.run_polling()


if __name__ == "__main__":
    main()
