from .feature import Feature


class Spaces(Feature):

    def score(self, value) -> float:
        return sum(c.isspace() for c in str(value))
