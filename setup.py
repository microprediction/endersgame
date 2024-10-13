

import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="endersgame",
    version="0.5.0",
    description="Online autonomous time series prediction of near martingales",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/microprediction/endersgame",
    author="microprediction",
    author_email="peter.cotton@microprediction.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.12",
    ],
    packages=["endersgame",
              "endersgame.accounting",
              "endersgame.attackers",
              "endersgame.datasources",
              "endersgame.examples",
              "endersgame.mixins",
              "endersgame.riverstats",
              "endersgame.syntheticdata",
              "endersgame.rivertransformers",
              "endersgame.runners"],
    test_suite='pytest',
    tests_require=['pytest','pandas_ta'],
    include_package_data=True,
    extras_require={"tests":["pandas_ta","flake8","pytest"]},
    install_requires=["numpy","river","requests","statsmodels"],
    entry_points={
        "console_scripts": [
            "endersgame=endersgame.__main__:main",
        ]
    },
)
