from setuptools import setup, find_packages
from os.path import abspath, dirname, join

# Fetches the content from README.md
# This will be used for the "long_description" field.
README_MD = open(join(dirname(abspath(__file__)), "README.md")).read()

setup(
    # The name of project.
    # pip install websiteclassificationapi
    name="websiteclassificationapi",

    # The version of your project.
    version="2.2",

    packages=find_packages(exclude="tests"),

    description="Website classification API",

    long_description=README_MD,

    long_description_content_type="text/markdown",

    url="https://github.com/websitecategorization/websiteclassificationnapi",

    author_name="Samo",
    author_email="info@websitecategorizationapi.com",

    # Classifiers help categorize your project.
    # For a complete list of classifiers, visit:
    # https://pypi.org/classifiers
    # This is OPTIONAL
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Environment :: GPU :: NVIDIA CUDA :: 11.3","Environment :: GPU :: NVIDIA CUDA :: 11.0", "Environment :: GPU :: NVIDIA CUDA",   "Environment :: GPU :: NVIDIA CUDA :: 11.2","Environment :: GPU :: NVIDIA CUDA :: 10.1", 
        "Programming Language :: Python :: 3 :: Only"
    ],

    keywords="website categorization, classification, categorization",
)