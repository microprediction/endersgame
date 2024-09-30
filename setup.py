

import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="endersgame",
    version="0.2.0",
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
              "endersgame.datasources",
              "endersgame.accounting",
              "endersgame.attackers",
              "endersgame.examples",
              "endersgame.syntheticdata",
              "endersgame.rivertransformers",
              "endersgame.riverstats",
                "endersgame.bot"],
    test_suite='pytest',
    tests_require=['pytest'],
    include_package_data=True,
    extras_require={"full":[]},
    install_requires=["numpy","river"],
    entry_points={
        "console_scripts": [
            "endersgame=endersgame.__main__:main",
        ]
    },
)
