from typing import Dict


class SimpleTypePredictor:
    """
        A simple type predictor is a predictor that
        tries to guess the type of an object by only
        using the string properties.

        This type of predictor mainly tries to avoid
        false negatives.
    """

    @property
    def name(self):
        """Return type identified by this predictor."""
        return self.__class__.__name__[:-4]

    @property
    def fuzzy(self) -> bool:
        """Return a boolean representing if predicted type is fuzzy or defined."""
        return False

    def validate(self, candidate, **kwargs: Dict) -> bool:
        """Return boolean representing if type is identified.

        Parameters
        -----------------------------------
        candidate,
            The candidate to be identified.
        kwargs:Dict,
            Additional features to be considered.
        """
        raise NotImplementedError(
            "Method validate must be implemented in child class."
        )

    def convert(self, candidate, **kwargs: Dict) -> bool:
        """Return candidate converted to type.

        Parameters
        -----------------------------------
        candidate,
            The candidate to be identified.
        kwargs:Dict,
            Additional features to be considered.
        """
        return candidate
