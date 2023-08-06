import compress_json


def load_local_json(path: str):
    return compress_json.local_load("{0}.json.gz".format(path))


def load_nan():
    return load_local_json("nan")


def load_provinces_codes():
    return load_local_json("ProvinceCode")


def load_regions():
    return load_local_json("Region")


def load_municipalities():
    return load_local_json("Municipality")


def load_countries():
    return load_local_json("Country")


def load_country_codes():
    return load_local_json("CountryCode")


def load_surnames():
    return load_local_json("Surname")


def load_names():
    return load_local_json("Name")


def load_caps():
    return load_local_json("CAP")


def load_generic_caps():
    return load_local_json("GenericCAP")


def load_codice_fiscale():
    return load_local_json("CodiceFiscale")


def load_iva():
    return load_local_json("IVA")


def load_strings():
    return load_local_json("String")


def load_email():
    return load_local_json("email")


def load_phone():
    return load_local_json("phone")


def load_date():
    return load_local_json("date")


def load_address():
    return load_local_json("Address")


def load_boolean():
    return load_local_json("Boolean")


def load_address_starters():
    return load_local_json("address_starters")


def load_biological_sex():
    return load_local_json("BiologicalSex")


def load_document_types():
    return load_local_json("Document")


def load_plate():
    return load_local_json("Plate")


def load_codice_catasto():
    return load_local_json("CodiceCatasto")


def load_currency_starters():
    return load_local_json("currency_starters")


def load_tax():
    return load_local_json("tax")
