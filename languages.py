from dataclasses import dataclass

@dataclass(frozen=True)
class Language:
    code: str      # BCP-47, used by Sarvam
    name: str
    native: str
    speaker: str = "shubh"   # Bulbul v3 default voice

# Only languages supported by STT + TTS + LLM together
SUPPORTED = {l.code: l for l in [
    Language("hi-IN", "Hindi", "हिन्दी"),
    Language("en-IN", "English", "English"),
    Language("mr-IN", "Marathi", "मराठी"),
    Language("gu-IN", "Gujarati", "ગુજરાતી"),
    Language("bn-IN", "Bengali", "বাংলা"),
    Language("ta-IN", "Tamil", "தமிழ்"),
    Language("te-IN", "Telugu", "తెలుగు"),
    Language("kn-IN", "Kannada", "ಕನ್ನಡ"),
    Language("ml-IN", "Malayalam", "മലയാളം"),
    Language("pa-IN", "Punjabi", "ਪੰਜਾਬੀ"),
    Language("od-IN", "Odia", "ଓଡ଼ିଆ"),
]}

def get_language(code: str) -> Language:
    return SUPPORTED.get(code, SUPPORTED["hi-IN"])