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
 
GEMINI_MODEL = "gemini-3.6-flash"
SYSTEM_PROMPT = """
Ești Laba de Urs 🐻, un bot de Telegram pentru un grup de prieteni.

Vorbești natural în limba română.
Ești foarte amuzant, faci caterincă și glume.
Poți folosi limbaj colocvial și vulgar moderat atunci când se potrivește.
Răspunsurile sunt de obicei scurte.

Nu răspunde la fiecare mesaj banal.
Dacă mesajul nu necesită răspuns, răspunde exact cu:
SKIP

Dacă cineva îți vorbește direct, te salută, pune o întrebare
sau face caterincă cu tine, răspunde natural.

Dacă cineva înjură, poți răspunde în stil de caterincă.
Nu amenința serios și nu încuraja violența reală.

Dacă cineva întreabă cine ești, spune că ești botul Laba de Urs.
"""

CUVINTE_INJURATURI = [
    "muie",
    "pula",
    "pulă",
    "coaie",
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

REPLICI = [
    "Taci, bă, că te-a auzit ursul 😂🐻",
    "Bă, ușor cu vocabularul, că se trezește ursul 😂🐻",
    "Gata, mă, iar ai pornit motorul de înjurături? 😂",
    "Băăă, ce limbaj ai azi 😂🐻",
    "Mai încet, campionule, că te vede Laba de Urs 😂🐻"
]


def contine_injuratura(text):
    text = text.lower()

    for cuvant in CUVINTE_INJURATURI:
        if cuvant in text:
            return True

    return False


def gemini_response(text):
    if not GEMINI_API_KEY:
        return "❌ GEMINI_API_KEY nu este setat!"

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
                + error.get(
                    "message",
                    "eroare necunoscută"
                )
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
            "text",
            ""
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

    if contine_injuratura(text):
        await update.message.reply_text(
            random.choice(REPLICI)
        )
        return

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
    print("🤖 Gemini:", GEMINI_MODEL)

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
