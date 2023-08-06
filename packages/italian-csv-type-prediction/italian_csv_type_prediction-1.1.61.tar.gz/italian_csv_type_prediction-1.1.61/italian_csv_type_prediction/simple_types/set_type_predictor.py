from .simple_type import SimpleTypePredictor
from ..utils import normalize
from typing import List


class SetTypePredictor(SimpleTypePredictor):

    def __init__(self, elements: List, normalize_values: bool = False):
        """Create new set based predictor.

        Parameters
        --------------------------------
        elements: List,
            List of elements to take in consideration.
        normalize_values: bool = False,
            Whetever to normalize elements.
        """
        self._normalize_values = normalize_values
        if self._normalize_values:
            elements = [
                normalize(element)
                for element in elements
            ]
        self._set = set(elements)

    def validate(self, candidate) -> bool:
        """Return boolean representing if given candidate is part of set."""
        return (
            normalize(candidate)
            if self._normalize_values
            else candidate
        ) in self._set
