from intents.Intent import Intent
from intents.intent_keywords import intent_keywords

def detect_intent(text: str, lang: str):
    text = text.lower().strip()
    for intent_key, languages in intent_keywords.items():
        keywords = languages.get(lang, [])

        for keyword in keywords:
            if text in keyword:
                print(Intent(intent_key))
                return Intent(intent_key)
    return Intent.UNKNOWN