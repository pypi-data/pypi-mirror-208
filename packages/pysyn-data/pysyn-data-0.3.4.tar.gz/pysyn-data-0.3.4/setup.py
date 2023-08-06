from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.3.4'
DESCRIPTION = 'This package is for generating synthetic data using 4 models i.e Conditional Genrative Adveserial Networks(CTGAN), Gaussian Mixture Model (GMM), Prinicipal Component Analysis (PCA) and Bayesian Network (BN). It also informs the user which model will work best based on the input data characterisitics.'
LONG_DESCRIPTION = 'This package is for generating synthetic data using 4 models i.e Conditional Genrative Adveserial Networks(CTGAN), Gaussian Mixture Model (GMM), Prinicipal Component Analysis (PCA) and Bayesian Network (BN). It also informs the user which model will work best based on the input data characterisitics. This package was created in TAVLAB under guidance of Dr. Tavpritesh Sethi (Computational Biology Lab under Dr Tavpritesh Sethi at IIITD) for Clinical Data Synthesis Project at Indraprastha Institute of Information Technology, Delhi.'

# Setting up
setup(
    name="pysyn-data",
    version=VERSION,
    author="Raghav-Ritesh-Tavlab",
    author_email="raghav.20.rb@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)