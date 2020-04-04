from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="autogen-backend",
    version="0.0.1",

    license="MIT",
    author="Fabian Keller",
    author_email='pypi.20.fkeller@spamgourmet.com',
    url="https://github.com/bluenote10/autogen-backend",

    description="DSL for auto-generating simple backends",
    long_description=long_description,
    long_description_content_type="text/markdown",

    install_requires=requirements,
    setup_requires=["pytest-runner"],
    tests_require=[
        "pytest",
        "pytest-cov",
    ],
    packages=find_packages(),

    # To make use of MANIFEST.in:
    include_package_data=True,
)
