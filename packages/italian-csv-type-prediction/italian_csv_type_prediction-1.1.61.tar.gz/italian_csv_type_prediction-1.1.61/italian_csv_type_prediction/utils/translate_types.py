import compress_json
import pandas as pd
import os
from typing import Tuple, List, Union
from .translator import Translator


class TranslateType:

    SUPPORTED_LANGUAGES = ("it", )

    def __init__(self, language: str = "it", error_handling: str = "raise"):
        """Create new object to translate types to given language.

        Parameters
        ----------------------
        language: str = "it",
            The language to translate the strings to.
            Currently supporting only italian language.
        error_handling: str = "raise",
            Behaviour of the translator when a given string is not available.
            The possible behaviours are 'raise' or 'pass'.
            The default behaviour is 'raise'.

        Raises
        ----------------------
        ValueError,
            When the given language is not supported.
        ValueError,
            When the given error handling is not supported.
        """
        if language not in TranslateType.SUPPORTED_LANGUAGES:
            raise ValueError(
                (
                    "Given language '{language}' is not supported. "
                    "The supported languages are {supported_languages}."
                ).format(
                    language=language,
                    supported_languages=", ".join(
                        TranslateType.SUPPORTED_LANGUAGES
                    )
                )
            )
        self._translator = Translator(
            path=os.path.join(
                os.path.dirname(__file__),
                "{}.json".format(language)
            ),
            error_handling=error_handling
        )

    def translate(self, value_type: Union[List, Tuple]) -> str:
        """Return value type translated to given language.

        Parameters
        ----------------------
        value_type: Union[str, List, Tuple],
            Either the value to be translated or a list of values.

        Raises
        ----------------------
        ValueError,
            If the value is not available in the dictionary.

        Returns
        ----------------------
        The translated value.
        """
        return self._translator.translate(value_type)

    def reverse_translate(self, value_type: Union[str, List, Tuple]) -> str:
        """Return value type translated back to english from given language.

        Parameters
        ----------------------
        value_type: Union[str, List, Tuple],
            Either the value to be back translated or a list of values.

        Raises
        ----------------------
        ValueError,
            If the value is not available in the dictionary.

        Returns
        ----------------------
        The back translated value.
        """
        return self._translator.reverse_translate(value_type)

    def translate_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Translate all dataframe."""
        return self._translator.translate_dataframe(df)
