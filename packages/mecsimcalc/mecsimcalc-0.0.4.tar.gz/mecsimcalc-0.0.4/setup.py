from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = "0.0.4"
DESCRIPTION = "Useful functions for MecSimCalc.com"
LONG_DESCRIPTION = "Useful functions for MecSimCalc.com"

# Setting up
setup(
    name="mecsimcalc",
    version=VERSION,
    author="MecSimCalc",
    author_email="<info@mecsimcalc.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=["Pillow", "pandas", "matplotlib"],
    keywords=["python", "MecSimCalc", "Calculator", "Simple"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    extras_require={
        "dev": ["pytest>=7.0", "twine >= 4.0.2"],
    },
)
