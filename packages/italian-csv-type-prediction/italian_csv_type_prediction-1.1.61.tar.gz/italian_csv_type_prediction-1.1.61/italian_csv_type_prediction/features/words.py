from .feature import Feature


class Words(Feature):

    def score(self, value) -> float:
        return sum(c.isalpha() for c in str(value))
