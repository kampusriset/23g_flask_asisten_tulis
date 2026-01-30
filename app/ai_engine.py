# app/ai_engine.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()


def call_ai(provider, prompt, temperature=0.25, max_tokens=2000, top_p=0.9):
    provider = provider.lower()

    try:
        # ================= GEMINI =================
        if provider == "gemini":
            key = os.getenv("GEMINI_API_KEY")
            if not key:
                return "Model Gemini belum tersedia."

            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={key}"

            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                    "topP": top_p
                }
            }

            r = requests.post(url, json=payload, timeout=20)
            r.raise_for_status()

            data = r.json()
            return (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )

        # ================= OPENAI =================
        elif provider == "openai":
            key = os.getenv("OPENAI_API_KEY")
            if not key:
                return "Model OpenAI belum tersedia."

            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}]
            }

            r = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=20
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]

        # ================= GROQ =================
        elif provider == "groq":
            key = os.getenv("GROQ_API_KEY")
            if not key:
                return "Model Groq belum tersedia."

            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "llama3-70b-8192",
                "messages": [{"role": "user", "content": prompt}]
            }

            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=20
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]

        # ================= DEEPSEEK =================
        elif provider == "deepseek":
            key = os.getenv("DEEPSEEK_API_KEY")
            if not key:
                return "Model DeepSeek belum tersedia."

            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}]
            }

            r = requests.post(
                "https://api.deepseek.com/chat/completions",
                headers=headers,
                json=payload,
                timeout=20
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]

        return "Model AI belum tersedia."

    except Exception as e:
        print(f"call_ai ERROR ({provider}):", e)
        return "Model AI belum tersedia."


# ===========================
# Helper prompt khusus notes
# ===========================
def note_suggest_prompt(text):
    last_words = text.split()[-3:]
    context = " ".join(last_words)
    return (
        "Lanjutkan teks berikut dengan 1 atau 2 kata saja.\n"
        "Contoh jawaban yang benar:\n"
        "- dan\n"
        "- sehingga\n"
        "- untuk itu\n\n"
        f"Teks:\n{context}\n\nJawaban:"
    )


def note_summarize_prompt(text):
    return (
        "Ringkas catatan berikut menjadi versi singkat, jelas, "
        "dan mudah dibaca. Jangan menambah informasi baru.\n\n"
        f"Catatan:\n{text}\n\nRingkasan:"
    )


def note_summarize_bullet_prompt(text):
    return (
        "Ringkas catatan berikut menjadi bullet point.\n"
        "- Gunakan 4 sampai 7 poin\n"
        "- Setiap poin singkat dan jelas\n"
        "- Jangan menambah informasi baru\n"
        "- Jangan pakai paragraf\n\n"
        f"Catatan:\n{text}\n\nBullet point:"
    )
