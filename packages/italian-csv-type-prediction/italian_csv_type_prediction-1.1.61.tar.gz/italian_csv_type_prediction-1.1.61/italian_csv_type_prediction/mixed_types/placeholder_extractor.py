import pandas as pd
from typing import Dict, List
from .name_surname_extractor import NameSurnameExtractor
from .surname_name_extractor import SurnameNameExtractor
from .address_extractor import AddressExtractor
from .default_extractor import DefaultExtractor
from .custom_string_extractor import CustomStringExtractor
from ..simple_types.string_type import StringType
from ..embedding import DataframeEmbedding
from ..exceptions import IllegalStateError
from ..utils import TranslateType


class PlaceholderExtractor:

    def __init__(
        self,
        language: str = None,
        custom_string_extractors: List[CustomStringExtractor] = None,
        fail_on_collision: bool = False
    ):
        """Create new placeholder extractor object.

        Parameters
        ---------------------------------
        language: str = None,
            Optional language to translate the types to.
            If you want to add languages that are not currently supported
            please consider doing a pull request to the github library.
        custom_string_extractors: List[CustomStringExtractor] = None,
            Optional list of custom placeholders to be used when a String
            type is encountered. The list will be evaluated top to bottom
            and the first extractor that validates the given
            string value will be used to extract its placeholders.
        fail_on_collision: bool = False,
            Whether to fail when a collision is detected.
        """
        translator = None if language is None else TranslateType(language)
        extractors = [
            extractor(
                translator=translator,
                fail_on_collision=fail_on_collision
            )
            for extractor in (
                NameSurnameExtractor,
                SurnameNameExtractor,
                AddressExtractor
            )
        ]
        self._string_type_name = StringType().name
        self._default = DefaultExtractor(translator)
        self._embedding = DataframeEmbedding()
        self._extractors = {
            extractor.name: extractor
            for extractor in extractors
        }
        self._custom_string_extractors = custom_string_extractors

    def _handle_value_extraction(self, candidate: str, candidate_type: str, **kwargs: Dict) -> Dict:
        """Return extraction of given candidate.

        Parameters
        ---------------------
        candidate: str,
            String candidate to be extracted.
        candidate_type: str,
            Type of the candidate.
        **kwargs: Dict,
            Additional metadata to be used while executing the extractions.

        Returns
        ---------------------
        Dictionary of metadata for given candidate.
        """
        try:
            # If the type of the candidate is a String
            if candidate_type == self._string_type_name and self._custom_string_extractors is not None:
                # If the custom string extractors are provided
                # we iterate over them and check if at least one validates the given candidate
                for custom_string_extractor in self._custom_string_extractors:
                    # If we get an extractor that validates the given value
                    if custom_string_extractor.validate(candidate, **kwargs):
                        # We return the extracted candidate
                        return custom_string_extractor.extract(candidate, candidate_type, **kwargs)

            return self._extractors.get(candidate_type, self._default).extract(
                candidate=candidate,
                candidate_type=candidate_type,
                **kwargs
            )
        except IllegalStateError:
            return self._default.extract(candidate, "Error")

    def extract(self, df: pd.DataFrame, types: pd.DataFrame) -> pd.DataFrame:
        fiscal_codes = self._embedding.get_fiscal_codes(df)
        italian_vat_codes = self._embedding.get_italian_vat_codes(df)
        return pd.DataFrame({
            column: [
                self._handle_value_extraction(
                    candidate=candidate,
                    candidate_type=candidate_type,
                    fiscal_code=fiscal_code,
                    italian_vat_code=italian_vat_code
                )
                for candidate, candidate_type, fiscal_code, italian_vat_code in zip(df[column], types[column], fiscal_codes, italian_vat_codes)
            ]
            for column in df.columns
        })
