import compress_json
import pandas as pd
from typing import Tuple, List, Union, Dict


class Translator:

    ERROR_HANDLING = ("raise", "pass")

    def __init__(self, path: str = None, dictionary: Dict = None, error_handling: str = "raise"):
        """Create new object to translate types to given language.

        Parameters
        ----------------------
        path: str = None,
            Path from where to load the dictionary.
        dictionary: Dict = None,
            Dictionary for the translations.
        error_handling: str = "raise",
            Behaviour of the translator when a given string is not available.
            The possible behaviours are 'raise' or 'pass'.
            The default behaviour is 'raise'.

        Raises
        ----------------------
        ValueError,
            When the given error handling is not supported.
        ValueError,
            When neither path or dictionary is given.
        ValueError,
            When both path and dictionary are given.
        """
        if dictionary is None and path is None:
            raise ValueError("Both given dictionary and path are none.")
        if dictionary is not None and path is not None:
            raise ValueError("Both given dictionary and path are not none.")
        self._translations = compress_json.load(
            path) if dictionary is None else dictionary
        self._error_handling = error_handling
        self._reverse_translations = {
            v: k
            for k, v in self._translations.items()
        }

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
        if isinstance(value_type, (list, tuple)):
            return tuple([
                self.translate(v)
                for v in value_type
            ])
        if value_type not in self._translations:
            if self._error_handling == "raise":
                raise ValueError(
                    "The given value {} is not available in the dictionary.".format(
                        value_type
                    )
                )
            if self._error_handling == "pass":
                return value_type
        return self._translations[value_type]

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
        if isinstance(value_type, (list, tuple)):
            return tuple([
                self._reverse_translations(v)
                for v in value_type
            ])
        if value_type not in self._reverse_translations:
            if self._error_handling == "raise":
                raise ValueError(
                    "The given value {} is not available in the dictionary.".format(
                        value_type
                    )
                )
            if self._error_handling == "pass":
                return value_type
        return self._reverse_translations[value_type]

    def translate_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Translate all dataframe."""
        return df.applymap(self.translate)
