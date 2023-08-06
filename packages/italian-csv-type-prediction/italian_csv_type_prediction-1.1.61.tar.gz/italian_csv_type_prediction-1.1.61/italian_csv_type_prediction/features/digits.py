from .feature import Feature


class Digits(Feature):

    def score(self, value) -> float:
        return sum(c.isdigit() for c in str(value))
