from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(
    name="traversaal",
    version="0.3",
    description="A semantic search package for hotel data",
    author="Traversaal",
    author_email="hello@traversaal.com",
    url="https://github.com/hamzafarooq",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "torch",
        "transformers",
        "flask",
    ],
)
