from .simple_type import SimpleTypePredictor
import numpy as np

class FloatType(SimpleTypePredictor):

    def __init__(self):
        """Create new float type predictor based on regex."""
        pass

    def convert(self, candidate, **kwargs):
        if isinstance(candidate, (float, int)):
            return candidate
        candidate = candidate.replace(",", ".")
        candidate = candidate.replace('.', "", (candidate.count('.')-1))
        return float(candidate)

    def validate(self, candidate, **kwargs) -> bool:
        """Return boolean representing if given candidate matches regex for float values."""
        if str(candidate) == "0":
            return True
        if isinstance(candidate, bool):
            return False
        if isinstance(candidate, (float, int)):
            return np.isfinite(candidate)
        candidate = str(candidate)
        if "." in candidate and any(len(sub) < 3 for sub in candidate.split(".")[1:-1]):
            return False
        if str(candidate).startswith("0") and not str(candidate).replace(",", ".").startswith("0."):
            return False
        try:
            candidate = self.convert(candidate)
            return np.isfinite(candidate)
        except (ValueError, OverflowError):
            return False
