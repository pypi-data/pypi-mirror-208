import os
import re
# To use a consistent encoding
from codecs import open as copen

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the relevant file
with copen(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


def read(*parts):
    with copen(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


__version__ = find_version("italian_csv_type_prediction", "__version__.py")

test_deps = [
    "pytest",
    "pytest-cov",
    "coveralls",
    "validate_version_code",
    "codacy-coverage"
]

extras = {
    'test': test_deps,
}

setup(
    name='italian_csv_type_prediction',
    version=__version__,
    description="Attempt at predicting common types in CSVs about Italian people and places using Spacy NLP tool.",
    long_description=long_description,
    url="https://github.com/LucaCappelletti94/italian_csv_type_prediction",
    author="LucaCappelletti94",
    author_email="cappelletti.luca94@gmail.com",
    # Choose your license
    license='MIT',
    python_requires='>3.5.2',
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    tests_require=test_deps,
    # Add here the package dependencies
    install_requires=[
        "pandas",
        "numpy",
        "python-stdnum",
        "tqdm",
        "postal",
        "python-codicefiscale",
        "scikit-learn",
        "compress_json",
        "compress_pickle==1.2.0",
        "validate_email",
        "phonenumbers",
        "unidecode",
        "random_csv_generator"
    ],
    extras_require=extras,
)
