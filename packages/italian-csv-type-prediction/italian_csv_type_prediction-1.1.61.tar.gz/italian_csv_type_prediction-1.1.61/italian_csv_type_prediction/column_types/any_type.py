from multiprocessing import Pool, cpu_count
from typing import Dict, List

import pickle
from .column_type_predictor import ColumnTypePredictor
from .single_type_column import (AddressType, BiologicalSexType, BooleanType,
                                 CadastreCodeType, CompanyType,
                                 CountryCodeType, CountryType, DateType,
                                 DocumentType, EMailType, FloatType,
                                 IntegerType, ItalianFiscalCodeType,
                                 ItalianVATType, ItalianZIPCodeType,
                                 MunicipalityType, NameSurnameType, NameType,
                                 NaNType, PhoneNumberType, PlateType,
                                 ProvinceCodeType, RegionType, StringType,
                                 SurnameNameType, SurnameType, TaxType,
                                 YearType)


class AnyTypePredictor:
    def __init__(self, use_multiprocessing: bool = True):
        """Create new AnyType Prediction.

        Parameters
        -----------------------
        use_multiprocessing: bool = True,
            Wether to use multiprocessing.
        """
        self._predictors = [
            predictor()
            for predictor in (
                AddressType, ItalianZIPCodeType, ItalianFiscalCodeType,
                CountryCodeType, CountryType, DateType, EMailType,
                TaxType, SurnameNameType, NameSurnameType,
                FloatType, IntegerType, ItalianVATType, DocumentType,
                MunicipalityType, NameType, NaNType, PhoneNumberType,
                ProvinceCodeType, RegionType, StringType, SurnameType,
                CompanyType, YearType, BiologicalSexType, BooleanType,
                PlateType, CadastreCodeType
            )
        ]
        self._use_multiprocessing = use_multiprocessing

    @property
    def supported_types(self):
        """Return list of currently supported types."""
        return [
            predictor.name
            for predictor in self._predictors
        ]

    @property
    def predictors(self) -> List[ColumnTypePredictor]:
        return self._predictors

    def _predict_values(self, kwargs: Dict):
        predictor = kwargs.pop("predictor")
        return predictor.validate(**kwargs)

    def predict_values(
        self,
        values: List,
        fiscal_codes: List[str] = (),
        italian_vat_codes: List[str] = (),
        **kwargs
    ) -> List[bool]:
        tasks = (
            dict(
                predictor=predictor,
                values=values,
                fiscal_codes=fiscal_codes,
                italian_vat_codes=italian_vat_codes,
                **kwargs
            )
            for predictor in self.predictors
        )
        if self._use_multiprocessing:
            with Pool(cpu_count()) as p:
                predictions = p.map(self._predict_values, tasks)
                p.close()
                p.join()
        else:
            predictions = [
                self._predict_values(task)
                for task in tasks
            ]
        return predictions

    def predict(self, values: List, fiscal_codes: List[str] = (), italian_vat_codes: List[str] = (), **kwargs) -> Dict[str, List[bool]]:
        """Return prediction from all available type."""
        return dict(zip(self.supported_types, self.predict_values(values, fiscal_codes, italian_vat_codes, **kwargs)))
