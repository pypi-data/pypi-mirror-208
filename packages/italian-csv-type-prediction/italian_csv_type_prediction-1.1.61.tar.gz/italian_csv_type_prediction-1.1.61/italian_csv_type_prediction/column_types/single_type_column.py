from ..simple_types import AddressType as SimpleAddressType
from ..simple_types import BiologicalSexType as SimpleBiologicalSexType
from ..simple_types import BooleanType as SimpleBooleanType
from ..simple_types import CadastreCodeType as SimpleCadastreCodeType
from ..simple_types import CountryCodeType as SimpleCountryCodeType
from ..simple_types import CountryType as SimpleCountryType
from ..simple_types import DateType as SimpleDateType
from ..simple_types import DocumentType as SimpleDocumentType
from ..simple_types import EMailType as SimpleEMailType
from ..simple_types import FloatType as SimpleFloatType
from ..simple_types import FuzzyAddressType as SimpleFuzzyAddressType
from ..simple_types import \
    FuzzyGenericItalianZIPCodeType as SimpleFuzzyGenericItalianZIPCodeType
from ..simple_types import \
    FuzzyItalianZIPCodeType as SimpleFuzzyItalianZIPCodeType
from ..simple_types import \
    GenericItalianZIPCodeType as SimpleGenericItalianZIPCodeType
from ..simple_types import IntegerType as SimpleIntegerType
from ..simple_types import ItalianFiscalCodeType as SimpleItalianFiscalCodeType
from ..simple_types import ItalianVATType as SimpleItalianVATType
from ..simple_types import ItalianZIPCodeType as SimpleItalianZIPCodeType
from ..simple_types import MunicipalityType as SimpleMunicipalityType
from ..simple_types import NameSurnameType as SimpleNameSurnameType
from ..simple_types import NameType as SimpleNameType
from ..simple_types import NaNType as SimpleNaNType
from ..simple_types import PhoneNumberType as SimplePhoneNumberType
from ..simple_types import PlateType as SimplePlateType
from ..simple_types import ProvinceCodeType as SimpleProvinceCodeType
from ..simple_types import RegionType as SimpleRegionType
from ..simple_types import StringType as SimpleStringType
from ..simple_types import SurnameNameType as SimpleSurnameNameType
from ..simple_types import SurnameType as SimpleSurnameType
from ..simple_types import TaxType as SimpleTaxType
from ..simple_types import YearType as SimpleYearType
from .set_type_column import SetTypeColumnPredictor
from ..simple_types import CompanyType as SimpleCompanyType


class AddressType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(
            SimpleAddressType(),
            generalizations=SimpleFuzzyAddressType()
        )


class BiologicalSexType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(SimpleBiologicalSexType())


class SurnameNameType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(
            SimpleSurnameNameType(),
            others=[
                SimpleNameSurnameType(),
                SimpleCompanyType()
            ]
        )


class NameSurnameType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(
            SimpleNameSurnameType(),
            others=[
                SimpleSurnameNameType(),
                SimpleCompanyType()
            ]
        )


class BooleanType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(SimpleBooleanType(), min_threshold=0.4)


class ItalianZIPCodeType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(
            SimpleItalianZIPCodeType(),
            generalizations=[
                SimpleFuzzyItalianZIPCodeType(),
                SimpleGenericItalianZIPCodeType(),
                SimpleFuzzyGenericItalianZIPCodeType()
            ]
        )


class ItalianFiscalCodeType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(
            SimpleItalianFiscalCodeType(),
            others=SimpleItalianVATType(),
            min_threshold=0.2
        )


class CompanyType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(
            SimpleCompanyType(),
            others=[
                SimpleNameSurnameType(),
                SimpleSurnameNameType(),
                SimpleNameType(),
                SimpleSurnameType()
            ],
            min_threshold=0.9
        )


class CadastreCodeType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(SimpleCadastreCodeType())


class CountryCodeType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(SimpleCountryCodeType())


class CountryType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(SimpleCountryType())


class DateType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(SimpleDateType())


class DocumentType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(SimpleDocumentType(), generalizations=SimpleStringType())


class EMailType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(SimpleEMailType())


class FloatType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(SimpleFloatType())


class IntegerType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(SimpleIntegerType())


class ItalianVATType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(
            SimpleItalianVATType(),
            others=SimpleItalianFiscalCodeType(),
            min_threshold=0.2
        )


class MunicipalityType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(SimpleMunicipalityType())


class NameType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(
            SimpleNameType(),
            others=[
                SimpleCompanyType()
            ]
        )


class NaNType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(SimpleNaNType(), min_threshold=0)


class PhoneNumberType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(SimplePhoneNumberType())


class PlateType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(SimplePlateType())


class ProvinceCodeType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(SimpleProvinceCodeType())


class RegionType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(SimpleRegionType())


class StringType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(SimpleStringType())


class SurnameType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(
            SimpleSurnameType(),
            others=[
                SimpleCompanyType()
            ]
        )


class YearType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(SimpleYearType())


class TaxType(SetTypeColumnPredictor):
    def __init__(self):
        """Create new Predictor based on a single type."""
        super().__init__(SimpleTaxType())
