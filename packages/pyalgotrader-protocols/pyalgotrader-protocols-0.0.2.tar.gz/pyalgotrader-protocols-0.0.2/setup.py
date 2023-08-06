import os
import pathlib
import setuptools


current_directory = os.path.dirname(os.path.realpath(__file__))

readme = pathlib.Path(f"{current_directory}/README.md")

with readme.open("r") as f:
    long_description = f.read()

setuptools.setup(
    include_package_data=True,
    data_files=[(current_directory, ["README.md", "LICENSE"])],
    name="pyalgotrader-protocols",
    version="0.0.2",
    description="PyAlgoTrader Protocols",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/krunaldodiya/pyalgotrader-protocols",
    author="Krunal Dodiya",
    author_email="kunal.dodiya1@gmail.com",
    packages=setuptools.find_packages(),
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
