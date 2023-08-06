import os
import sys
from ast import parse

from setuptools import setup

if sys.version_info < (3, 7):
    print("vectice requires Python 3 version >= 3.7", file=sys.stderr)
    sys.exit(1)

package_root = os.path.abspath(os.path.dirname(__file__))

version_requires = ">=3.7.1"

with open(os.path.join("src", "vectice", "__version__.py")) as f:
    version = parse(next(line for line in f if line.startswith("__version__"))).body[0].value.s

with open("README.md", encoding="utf-8") as readme_file:
    readme = readme_file.read()

setup(
    name="vectice",
    version=version,
    description="Vectice Python library",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Vectice Inc.",
    author_email="sdk@vectice.com",
    url="https://www.vectice.com",
    package_data={"vectice": ["py.typed"]},
    license="Apache License 2.0",
    keywords=["Vectice", "Client", "API", "Adapter"],
    platforms=["Linux", "MacOS X", "Windows"],
    python_requires=version_requires,
    install_requires=[
        "python-dotenv>=0.11.0",
        "requests>=2.5.0",
        "rich",
        "urllib3",
        "gql[requests]",
        "GitPython",
        "packaging",
        "Pillow",
        "pandas",
    ],
    extras_require={
        "dev": [
            "black",
            "gitpython",
            "mypy",
            "ruff",
            "types-requests",
            "types-urllib3",
            "types-mock",
            "boto3-stubs[essential]",
        ],
        "doc": [
            "black",
            "markdown-callouts>=0.2",
            "markdown-exec>=1.2",
            "mkdocs>=1.3",
            "mkdocs-material>=7.3",
            "mkdocs-redirects>=1.2",
            "mkdocs-section-index>=0.3",
            "mkdocstrings[python]>=0.18",
        ],
        "test": [
            "docker-compose",
            "dslr[psycopg2-binary]",
            "mock>=1.0.1",
            "numpy",
            "pytest",
            "pytest-randomly",
            "coverage",
            "pytest-cov",
            "scikit-learn<=0.24.2",
            "testcontainers",
            "testbook",
            "db-dtypes>=1.1.1",
        ],
        "gcs": ["google-cloud-storage>=1.17.0", "google-cloud-bigquery"],
        "s3": ["boto3"],
    },
    classifiers=[
        "Topic :: Internet",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Typing :: Typed",
    ],
)
