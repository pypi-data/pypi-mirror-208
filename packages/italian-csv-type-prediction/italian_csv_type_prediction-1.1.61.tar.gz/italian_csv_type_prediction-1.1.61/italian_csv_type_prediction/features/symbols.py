from .feature import Feature
from .digits import Digits
from .words import Words
from .spaces import Spaces


class Symbols(Feature):

    def __init__(self):
        self._not_symbols = (
            Digits(),
            Words(),
            Spaces()
        )

    def score(self, value) -> float:
        s = str(value)
        return len(s) - sum([
            feature.score(s)
            for feature in self._not_symbols
        ])