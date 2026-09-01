import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

MODEL = "gemini-3.6-flash"

SYSTEM_PROMPT = """
Ești Laba de Urs 🐻, un bot de Telegram pentru caterincă.

Vorbești în limba română, natural, scurt și amuzant.
Îți place caterinca și glumele între prieteni.
Poți folosi limbaj vulgar moderat atunci când se potrivește glumei.

Dacă cineva te salută sau îți vorbește direct, răspunde.

Dacă cineva înjură, răspunde în stil de caterincă.

Nu amenința serios și nu încuraja violența reală.

Dacă mesajul nu necesită răspuns, răspunde exact:
SKIP
"""

def ask_gemini(text):

    url = "https://generativelanguage.googleapis.com/v1beta/interactions"

    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "input": text,
        "system_instruction": SYSTEM_PROMPT
    }

    try:
        r = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=30
        )

        result = r.json()

        print("Gemini status:", r.status_code)
        print("Gemini response:", result)

        if r.status_code != 200:
            error = result.get("error", {})
            return "❌ Gemini: " + error.get(
                "message",
                "eroare necunoscută"
            )

        # Caută textul răspunsului
        if "outputs" in result:
            for output in result["outputs"]:
                if output.get("type") == "text":
                    return output.get("text", "").strip()

        if "output" in result:
            output = result["output"]

            if isinstance(output, str):
                return output.strip()

            if isinstance(output, list):
                for item in output:
                    if item.get("type") == "text":
                        return item.get("text", "").strip()

        return "SKIP"

    except Exception as e:
        print("Gemini error:", e)
        return "❌ Eroare Gemini: " + str(e)


async def mesaj(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    if not update.message.text:
        return

    text = update.message.text

    raspuns = ask_gemini(text)

    if not raspuns:
        return

    if raspuns == "SKIP":
        return

    await update.message.reply_text(raspuns)


def main():

    if not TOKEN:
        print("❌ BOT_TOKEN lipsește!")
        return

    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY lipsește!")
        return

    print("🐻 LABA DE URS PORNITĂ!")
    print("🤖 MODEL:", MODEL)

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            mesaj
        )
    )

    app.run_polling()


if __name__ == "__main__":
    main()

În "requirements.txt":

python-telegram-bot
requests
