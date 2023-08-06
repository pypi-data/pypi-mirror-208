from setuptools import setup, find_namespace_packages

with open("requirements.txt") as requirements_file:
    requirements = requirements_file.read().splitlines()

with open("README.md") as description_file:
    long_description = description_file.read()

setup(
    name="tarvis-indicators-webapi",
    version="0.9.6",
    author="Tarvis Labs",
    author_email="python@tarvislabs.com",
    url="https://tarvislabs.com/",
    description="Tarvis Web API Indicators Library",
    long_description=long_description,
    packages=find_namespace_packages(include=["tarvis.*"]),
    python_requires=">=3.10",
    install_requires=requirements,
)
