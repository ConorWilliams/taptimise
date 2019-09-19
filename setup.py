# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""


import re
from setuptools import setup


version = re.search('^__version__\s*=\s*"(.*)"',
                    open('taptimise/__init__.py').read(), re.M).group(1)


with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")


setup(
    name="taptimise",
    packages=["taptimise"],
    entry_points={
        "console_scripts": ['taptimise = taptimise.taptimise:main']
    },
    install_requires=['tqdm', 'csv', 'numpy', 'pyfiglet', 'matplotlib'],
    version=version,
    description="Second generation tap optimisation algorithm for the eWaterPay project.",
    long_description=long_descr,
    author="Conor Williams",
    author_email="conorwilliams@outlook.com",
    url="https://github.com/ConorWilliams/taptimise",
)
