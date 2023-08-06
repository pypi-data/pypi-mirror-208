italian_csv_type_prediction
=========================================================================================
|travis| |sonar_quality| |sonar_maintainability| |codacy|
|code_climate_maintainability| |pip| |downloads|

This package is an attempt at predicting common types in CSVs about Italian people
and places using ensemble heuristics with Decision Random Forests and Spacy NLP tool.

How do I install this package?
----------------------------------------------
As usual, just download it using pip:

.. code:: shell

    apt-get update -y
    apt-get install -qyy apt-utils build-essential software-properties-common locales locales-all curl autoconf automake libtool python-dev pkg-config
    curl https://raw.githubusercontent.com/LucaCappelletti94/italian_csv_type_prediction/master/setup.sh | sh
    
    pip install italian_csv_type_prediction

Tests Coverage
----------------------------------------------
Since some software handling coverages sometimes
get slightly different results, here's three of them:

|coveralls| |sonar_coverage| |code_climate_coverage|

Usage examples
----------------------------------------------
To get the typization of a list of data you can use:

.. code:: python

    from italian_csv_type_prediction import predict_types

    predictions = predict_types([
        #list of words to predict goes here
    ])


.. |travis| image:: https://travis-ci.org/LucaCappelletti94/italian_csv_type_prediction.png
   :target: https://travis-ci.org/LucaCappelletti94/italian_csv_type_prediction
   :alt: Travis CI build

.. |sonar_quality| image:: https://sonarcloud.io/api/project_badges/measure?project=LucaCappelletti94_italian_csv_type_prediction&metric=alert_status
    :target: https://sonarcloud.io/dashboard/index/LucaCappelletti94_italian_csv_type_prediction
    :alt: SonarCloud Quality

.. |sonar_maintainability| image:: https://sonarcloud.io/api/project_badges/measure?project=LucaCappelletti94_italian_csv_type_prediction&metric=sqale_rating
    :target: https://sonarcloud.io/dashboard/index/LucaCappelletti94_italian_csv_type_prediction
    :alt: SonarCloud Maintainability

.. |sonar_coverage| image:: https://sonarcloud.io/api/project_badges/measure?project=LucaCappelletti94_italian_csv_type_prediction&metric=coverage
    :target: https://sonarcloud.io/dashboard/index/LucaCappelletti94_italian_csv_type_prediction
    :alt: SonarCloud Coverage

.. |coveralls| image:: https://coveralls.io/repos/github/LucaCappelletti94/italian_csv_type_prediction/badge.svg?branch=master
    :target: https://coveralls.io/github/LucaCappelletti94/italian_csv_type_prediction?branch=master
    :alt: Coveralls Coverage

.. |pip| image:: https://badge.fury.io/py/italian_csv_type_prediction.svg
    :target: https://badge.fury.io/py/italian_csv_type_prediction
    :alt: Pypi project

.. |downloads| image:: https://pepy.tech/badge/italian_csv_type_prediction
    :target: https://pepy.tech/badge/italian_csv_type_prediction
    :alt: Pypi total project downloads

.. |codacy| image:: https://api.codacy.com/project/badge/Grade/b7f2b7fbc54a424f8786d0602b8dd13e
    :target: https://www.codacy.com/manual/LucaCappelletti94/italian_csv_type_prediction?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=LucaCappelletti94/italian_csv_type_prediction&amp;utm_campaign=Badge_Grade
    :alt: Codacy Maintainability

.. |code_climate_maintainability| image:: https://api.codeclimate.com/v1/badges/92e64629c7cf783b39ab/maintainability
    :target: https://codeclimate.com/github/LucaCappelletti94/italian_csv_type_prediction/maintainability
    :alt: Maintainability

.. |code_climate_coverage| image:: https://api.codeclimate.com/v1/badges/92e64629c7cf783b39ab/test_coverage
    :target: https://codeclimate.com/github/LucaCappelletti94/italian_csv_type_prediction/test_coverage
    :alt: Code Climate Coverate
