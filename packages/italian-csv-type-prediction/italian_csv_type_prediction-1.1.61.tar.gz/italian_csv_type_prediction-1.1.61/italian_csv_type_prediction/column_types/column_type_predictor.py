from typing import Dict, List


class ColumnTypePredictor:
    """
        A column type predictor is a predictor that
        tries to guess the type of an object by extrapolating
        on the type of the othe objects of the same column.

        This type of predictor mainly tries to avoid
        false negatives.
    """

    @property
    def name(self):
        """Return type identified by this predictor."""
        return self.__class__.__name__[:-4]

    def validate(self, values: List, **kwargs: Dict) -> List[bool]:
        """Return list of booleans representing if each value has been identified.

        Parameters
        -----------------------------------
        values:List,
            List of other values in the column.
        kwargs:Dict,
            Additional features to be considered.
        """
        raise NotImplementedError(
            "Method validate must be implemented in child class."
        )
