# app/ai_engine.py
import requests
from app.services.ai_key_service import get_api_key


def call_ai(provider, prompt, temperature=0.25, max_tokens=2000, top_p=0.9):
    provider = provider.lower().strip()

    try:
        # ================= GEMINI =================
        if provider == "gemini":
            key = get_api_key("gemini")
            if not key:
                return "Model Gemini belum aktif."

            url = (
                "https://generativelanguage.googleapis.com/v1/models/"
                f"gemini-2.5-flash:generateContent?key={key}"
            )

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
            key = get_api_key("openai")
            if not key:
                return "Model OpenAI belum aktif."

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
            key = get_api_key("groq")
            if not key:
                return "Model Groq belum aktif."

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
            key = get_api_key("deepseek")
            if not key:
                return "Model DeepSeek belum aktif."

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
        return "Terjadi kesalahan saat menghubungi AI."
