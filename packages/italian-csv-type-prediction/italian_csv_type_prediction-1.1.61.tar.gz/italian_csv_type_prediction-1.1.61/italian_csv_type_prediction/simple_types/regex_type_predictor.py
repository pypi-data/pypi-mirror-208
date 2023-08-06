from .simple_type import SimpleTypePredictor
from ..utils import normalize
import re
from typing import List, Union


class RegexTypePredictor(SimpleTypePredictor):

    def __init__(self, pattern: Union[List[str], str]):
        """Create new regex based predictor.

        Parameters
        --------------------------------
        pattern: Union[List[str], str],
            The pattern against which to test.
        """
        if isinstance(pattern, list):
            pattern = "|".join(
                "({})".format(p)
                for p in pattern
            )
        self._regex = re.compile(pattern)

    def validate(self, candidate, **kwargs) -> bool:
        """Return boolean representing if given candidate matches regex."""
        return bool(self._regex.findall(normalize(str(candidate))))
