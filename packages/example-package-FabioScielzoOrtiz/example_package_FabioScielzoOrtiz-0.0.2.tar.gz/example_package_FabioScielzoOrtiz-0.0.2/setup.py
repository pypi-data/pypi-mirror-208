from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="example_package_FabioScielzoOrtiz",
    version="0.0.2",
    author="Fabio Scielzo Ortiz",
    author_email="fabioscielzo98@gmail.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FabioScielzoOrtiz/Distances_Package",  # add your project URL here
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
