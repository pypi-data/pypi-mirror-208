import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kaiko_research",
    version="0.0.9",
    author="Evgeny Ryabchenkov",
    author_email="evgeny.ryabchenkov@kaiko.com",
    description="An API wrapper for Kaiko data containing the information about data exports, parameters for each export and methods to fetch raw data or pre-processed data based on experience of Kaiko research intelligence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kaikodata/research-scripts",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=[
        "cerberus",
        "dask",
        "datetime",
        "pandas",
        "requests",
        "tqdm",
    ],
)
