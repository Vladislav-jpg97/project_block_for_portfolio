from transliterate import translit
import re
from transliterate.exceptions import LanguageDetectionError


def _transliterate(text: str) -> str:
    try:
        return translit(text, reversed=True)
    except LanguageDetectionError:
        return text


class SlugGenerationL:
    def generate(
            self,
            text: str,
    ):
        text = _transliterate(text)
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r"[\s_]+", "-", text)
        text = re.sub(r"^-+|-+$", "", text)
        return text
slug_generate = SlugGenerationL()
