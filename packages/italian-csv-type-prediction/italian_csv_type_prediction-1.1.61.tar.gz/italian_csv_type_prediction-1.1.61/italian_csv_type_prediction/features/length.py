from .feature import Feature


class Length(Feature):

    def score(self, value)->float:
        return len(str(value))