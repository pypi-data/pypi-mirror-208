from unidecode import unidecode


def normalize(candidate: str) -> str:
    if not isinstance(candidate, str):
        return candidate
    return " ".join(unidecode(candidate).lower().strip().replace("_", " ").replace("-", " ").split())
