

import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="midone",
    version="1.0.1",
    description="Online autonomous time series prediction of near martingales",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/microprediction/midone",
    author="microprediction",
    author_email="peter.cotton@microprediction.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.12",
    ],
    packages=["midone",
              "midone.accounting",
              "midone.attackers",
              "midone.datasources",
              "midone.examples",
              "midone.mixins",
              "midone.riverstats",
              "midone.syntheticdata",
              "midone.rivertransformers",
              "midone.runners"],
    test_suite='pytest',
    tests_require=['pytest','pandas_ta'],
    include_package_data=True,
    extras_require={"tests":["pandas_ta","flake8","pytest"]},
    install_requires=["numpy","river","requests","statsmodels"],
    entry_points={
        "console_scripts": [
            "midone=midone.__main__:main",
        ]
    },
)
