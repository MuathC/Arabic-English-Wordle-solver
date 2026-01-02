def remove_ascii(word: str) -> str:
    return ''.join(ch for ch in word if not ch.isascii())

def remove_tashkeel(word: str) -> str:
    tashkeel_chars = [
        "َ",  # fatha
        "ُ",  # dhamma
        "ِ",  # kasra
        "ْ",  # sukoon
        "ّ",  # shadda
        "ً",  # tanween
        "ٌ",  # tanween dham
        "ٍ",  # tanween kasr
        "ـ"   # char extender
    ]
    for char in tashkeel_chars:
        word = word.replace(char, "")
    return word

def remove_tashkeel_and_ascii(word: str) -> str:
    return remove_ascii(remove_tashkeel(word))
