import pathlib

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()

# Read long description from the readme.md file
with open("README.md",encoding='utf-8') as f:
    readme = f.read()

with open("LICENSE",encoding='utf-8') as f:
    license_text = f.read()

setup(
    name="npgbq",
    version="2.1.9",
    description="A package designed for helping everyone in the team to work with data ingestion",
    long_description_content_type="text/markdown",
    long_description=readme,
    author="Nopporn Phantawee",
    author_email="n.phantawee@gmail.com",
    url="https://github.com/noppGithub/npgbq",
    license="MIT",
    packages=find_packages(exclude=("tests", "docs")),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    install_requires=[
        "fastparquet",
        "google-cloud-bigquery",
        "google-cloud-logging",
        "openpyxl",
        "pandas",
        "pyarrow",
        "requests",
        "psycopg2-binary",
        "pyodbc",
        "db-dtypes",
    ],
    extras_require={
        "dev": ["check-manifest"],
        "test": ["coverage"],
    },
    python_requires=">=3.6, <4",
)
