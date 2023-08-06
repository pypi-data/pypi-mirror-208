from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="jschemator",
    version="0.0.3",
    description="A class interface for data modeling with json-schema",
    long_description=long_description,
    packages=find_packages(include=["jschemator"]),
    install_requires=[],
    extras_require={
        "dev": ["pytest", "pytest-cov", "pytest-asyncio", "aiosow"]
    },
)
