from distutils.util import convert_path

import setuptools

version = {}
with open(convert_path("gantry/version.py")) as fp:
    exec(fp.read(), version)


install_requires = [
    "datasets~=2.7.0",
    "Jinja2~=3.1.2",
    "aiohttp~=3.8",
    # 1.1.1 contains a fix for a regression in a dependency
    # https://stackoverflow.com/a/71574145
    "dateparser~=1.1,>=1.1.1",
    "typeguard~=2.13",
    "boto3-extensions>=0.11.0",
    "backoff~=2.1.2",
    "cachetools~=4.2",
    "click>=7.1.2",
    "click-aliases~=1.0",
    "click-spinner>=0.1.10",
    "requests>=2.22.0",
    "pyyaml>=5.3.1",
    "colorama>=0.4.0",
    "label-studio-sdk>=0.0.19,<0.0.22",
    "marshmallow>=3.11.1",
    "marshmallow-oneofschema>=3.0.1",
    "monotonic>=1.4",
    "tabulate~=0.8",
    "typing-extensions~=4.0",
    "tqdm~=4.64",
    "halo~=0.0.31",
    "isodate~=0.6",
    "pydantic==1.9.0",
    "python-dateutil>=2.8.1",
    "pandas",
    "numpy",
]


# https://packaging.python.org/tutorials/packaging-projects/
setuptools.setup(
    name="gantry",
    version=version["__version__"],
    install_requires=install_requires,
    include_package_data=True,
    author="Gantry Systems, Inc.",
    author_email="oss@gantry.io",
    description="Gantry Python Library",
    long_description="",
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    license="Apache Software License v2",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": ["gantry-cli = gantry.cli.main:cli"],
    },
    package_data={"": ["dataset/templates/*.jinja"]},
)
