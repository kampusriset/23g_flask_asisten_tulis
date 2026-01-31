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
