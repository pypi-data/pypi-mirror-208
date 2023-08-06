from .column_type_predictor import ColumnTypePredictor
from ..simple_types.simple_type import SimpleTypePredictor
from ..simple_types.nan_type import NaNType
from typing import List, Dict


class SetTypeColumnPredictor(ColumnTypePredictor):
    def __init__(
        self,
        main: SimpleTypePredictor,
        others: List[SimpleTypePredictor] = (),
        min_threshold: float = 0.6,  # [4 out of 5]
        fuzzy_generalization_threshold: float = 0.9,
        generalizations: List[SimpleTypePredictor] = ()
    ):
        """Create new Predictor based on a set.

        Predictors
        ----------------------------------
        main: SimpleTypePredictor,
            The main predictor to use.
        others: List[SimpleTypePredictor] = (),
            The other predictors that are allowed in this column.
            For instance often in CodiceFiscale columns there
            are often italian_vat_code codes.
        min_threshold: float = 0.9,
            Minimal amount of predictions of either main, others
            to accept the predictions as correct.
            This percentage excludes values that are identified as NaN values.
        fuzzy_generalization_threshold: float = 0.9,
            Minimal amount of predictions of main (only main, not others)
            to generalize the type to the values that are accept by any of
            the predictors specified in the generalizations parameter.
        generalizations: List[SimpleTypePredictor] = ()
            List of predictors that accept the type when main predictor
            is fuzzy and the predicted elements are more than the fuzzy
            generalization threshold.
        """
        self._main = main

        # We normalize the others and generalizations parameters
        # for when they are a single predictor.
        if isinstance(others, SimpleTypePredictor):
            others = (others,)
        if isinstance(generalizations, SimpleTypePredictor):
            generalizations = (generalizations,)

        self._others = others
        self._generalizations = generalizations
        self._min_threshold = min_threshold
        self._fuzzy_generalization_threshold = fuzzy_generalization_threshold
        self._nan = NaNType()

    def validate(self, values: List, fiscal_codes: List = None, italian_vat_codes: List = None, **kwargs: Dict) -> List[bool]:
        """Return list of booleans representing if each value has been identified.

        Parameters
        -----------------------------------
        values:List,
            List of other values in the column.
        kwargs:Dict,
            Additional features to be considered.

        Returns
        -----------------------------------
        Returns list of boolean predictions.
        """
        is_main_type = []
        is_other_type = []
        is_generalization = []
        is_nan_type = []

        # We iterate on every available value
        for i, value in enumerate(values):
            fiscal_code = fiscal_codes[i] if fiscal_codes is not None else None
            italian_vat_code = italian_vat_codes[i] if italian_vat_codes is not None else None
            # If the value is of the main type
            if self._main.validate(value, fiscal_code=fiscal_code, italian_vat_code=italian_vat_code, **kwargs):
                is_main_type.append(True)
                is_other_type.append(False)
                # The type itself is considered a generalization
                # of itself so to avoid another loop afterwards
                is_generalization.append(True)
                is_nan_type.append(False)
                continue
            # Or is from any of the other given valid types
            if any(other.validate(value, fiscal_code=fiscal_code, italian_vat_code=italian_vat_code, **kwargs) for other in self._others):
                is_main_type.append(False)
                is_other_type.append(True)
                is_generalization.append(False)
                is_nan_type.append(False)
                continue
            # Or finally the value can be a NaN
            if self._nan.validate(value, fiscal_code=fiscal_code, italian_vat_code=italian_vat_code, **kwargs):
                is_main_type.append(False)
                is_other_type.append(False)
                is_generalization.append(False)
                is_nan_type.append(True)
                continue
            if any(
                generalization.validate(
                    value,
                    fiscal_code=fiscal_code,
                    italian_vat_code=italian_vat_code, **kwargs
                )
                for generalization in self._generalizations
            ):
                is_main_type.append(False)
                is_other_type.append(False)
                is_generalization.append(True)
                is_nan_type.append(False)
                continue
            # Otherwise no type at all was detected
            # from the considered ones.
            is_main_type.append(False)
            is_other_type.append(False)
            is_generalization.append(False)
            is_nan_type.append(False)

        only_main = sum(is_main_type)
        only_others = sum(is_other_type)
        only_nan = sum(is_nan_type)
        total_values = len(values)

        # If the identified values, removed the known values that are
        # known to happen in the same column such as others or NaN
        # are less than a given percentage, we consider the eventual
        # positive matches as false positives.
        if only_main <= (total_values - only_others - only_nan) * self._min_threshold:
            return [False]*total_values

        # If the identified values are above a given percentage of the values
        # of the same column, and the Predictor used is caracterized by false negatives
        # with the "fuzzy" property, we extend the predictions to the
        # values that are predicted by any of the generalizations.
        if only_main > (total_values - only_nan)*self._fuzzy_generalization_threshold:
            is_main_type = is_generalization

        return is_main_type
