from typing import Dict, List
from .simple_type import SimpleTypePredictor
from .boolean_type import BooleanType
from .biological_sex_type import BiologicalSexType
from .cadastre_code_type import CadastreCodeType
from .country_code_type import CountryCodeType
from .country_type import CountryType
from .date_type import DateType
from .document_type import DocumentType
from .email_type import EMailType
from .float_type import FloatType
from .integer_type import IntegerType
from .italian_fiscal_code_type import ItalianFiscalCodeType
from .italian_vat_type import ItalianVATType
from .italian_zip_code_type import ItalianZIPCodeType
from .municipality_type import MunicipalityType
from .nan_type import NaNType
from .phone_number_type import PhoneNumberType
from .plate_type import PlateType
from .province_code_type import ProvinceCodeType
from .region_type import RegionType
from .string_type import StringType
from .tax_type import TaxType
from .year_type import YearType
from .address_type import AddressType
from .name_type import NameType
from .surname_type import SurnameType


class AnyTypePredictor:
    def __init__(self):
        predictors = [
            predictor()
            for predictor in (
                AddressType, ItalianZIPCodeType, ItalianFiscalCodeType, CountryCodeType,
                CountryType, DateType, EMailType, TaxType,
                FloatType, IntegerType, ItalianVATType, DocumentType,
                MunicipalityType, NameType, NaNType, PhoneNumberType,
                ProvinceCodeType, RegionType, StringType, SurnameType,
                YearType, BiologicalSexType, BooleanType, PlateType, CadastreCodeType
            )
        ]
        self._predictors = {
            predictor.name: predictor
            for predictor in predictors
        }

    @property
    def supported_types(self):
        """Return list of currently supported types."""
        return list(self._predictors.keys())

    def supports(self, predictor_type: str) -> bool:
        """Return boolean representing if predictor_type is supported.

        Parameters
        --------------------------
        predictor_type: str,
            Type to check the support for.

        Returns
        --------------------------
        Boolean true if type is supported.
        """
        return predictor_type in self._predictors

    def convert(self, predictor: str, value: str) -> bool:
        """Return converted result on given predictor for given value.

        Parameters
        -------------------
        predictor: str,
            Name of the predictor to use.
        value: str,
            Value to validate.

        Raises
        -------------------
        ValueError,
            If given predictor is not currently supported.

        Returns
        -------------------
        The converted result.
        """
        if predictor not in self._predictors:
            raise ValueError(
                "Given predictor {} is not currently supported".format(
                    predictor
                )
            )
        return self._predictors[predictor].convert(value)

    def validate(self, predictor: str, value: str, fuzzy_as_true: bool = False, **kwargs: Dict) -> bool:
        """Return validation result on given predictor for given value.

        Parameters
        -------------------
        predictor: str,
            Name of the predictor to use.
        value: str,
            Value to validate.
        fuzzy_as_true: bool = False,
            Wethever to consider any fuzzy predictor as tautological.
            By default false.
        **kwargs: Dict,
            Metadata to be optionally used to validate the candidate.

        Raises
        -------------------
        ValueError,
            If given predictor is not currently supported.

        Returns
        -------------------
        The validation result.
        """
        if predictor not in self._predictors:
            raise ValueError(
                "Given predictor {} is not currently supported".format(
                    predictor
                )
            )
        if fuzzy_as_true and self._predictors[predictor].fuzzy:
            return True
        return self._predictors[predictor].validate(value, **kwargs)
