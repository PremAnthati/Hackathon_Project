from deep_translator import GoogleTranslator

def translate_text(text: str, src: str = 'te', dest: str = 'en') -> str:
    try:
        translated = GoogleTranslator(source=src, target=dest).translate(text)
        return translated
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Fallback to original text if fails

