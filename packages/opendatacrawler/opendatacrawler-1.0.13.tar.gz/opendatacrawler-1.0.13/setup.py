import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="opendatacrawler",
    version="1.0.13",
    description="Crawler for open data portals",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/aberenguerpas/OpenDataCrawler/",
    author="Alberto Berenguer Pastor",
    author_email="alberto.berenguer@ua.es",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(),
    include_package_data=True,
    package_data={'opendatacrawler': ['intro.txt']},
    install_requires=["tqdm","sodapy"],
    entry_points={
        "console_scripts": [
            "crawler=opendatacrawler.__main__:main",
        ]
    },
)