from .string_type import SimpleTypePredictor
from ..datasets import load_address_starters
from ..utils import normalize


class AddressType(SimpleTypePredictor):

    def __init__(self):
        self._words = load_address_starters()

    @property
    def fuzzy(self) -> bool:
        return True

    def validate(self, candidate, **kwargs) -> bool:
        candidate = normalize(str(candidate))
        return any(candidate.startswith(e) for e in self._words)
