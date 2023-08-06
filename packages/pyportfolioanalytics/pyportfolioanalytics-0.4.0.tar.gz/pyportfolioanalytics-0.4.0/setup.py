import pathlib
from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent

VERSION = '0.4.0'
PACKAGE_NAME = 'pyportfolioanalytics'
AUTHOR = 'Sebastian Marat Urdanegui Bisalaya'
AUTHOR_EMAIL = 'sebasurdanegui@gmail.com'
URL = 'https://github.com/SebastianUrdaneguiBisalaya/py-portfolioanalytics'

LICENSE = 'MIT'
DESCRIPTION = 'Librería para leer ficheros PDFs y extraer la información en formato str'
LONG_DESC_TYPE = "text/markdown"


INSTALL_REQUIRES = [
      'pandas', 'numpy', 'matplotlib', 'seaborn',
      'yfinance', 'reportlab'
      ]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    install_requires=INSTALL_REQUIRES,
    license=LICENSE,
    packages=find_packages(),
    include_package_data=True
)