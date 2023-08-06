from setuptools import setup, find_packages

setup(
    name="traversaal",
    version="0.1",
    description="A semantic search package for hotel data",
    author="Traversaal",
    author_email="hello@traversaal.com",
    url="https://github.com/traversaal",
    packages=find_packages(),
    install_requires=[
        "torch",
        "transformers",
        "flask",
    ],
)
