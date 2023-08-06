import os
import setuptools

with open("README_public.md", "r") as fh:
    long_description = fh.read()

with open("PYSPARK_VERSION", "r") as f:
    pyspark_version = f.read()

with open("TD_PYSPARK_VERSION", "r") as f:
    version = f.read()

setuptools.setup(
    name=os.environ.get('PROJECT_NAME',"td_pyspark"),
    version=version,
    description="Treasure Data extension for pyspark",
    author="Treasure Data",
    author_email="dev+pypi@treasure-data.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://docs.treasuredata.com/display/public/INT/Data+Science+and+SQL+Tools",
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={"": ["*.jar"]},
    license="Apache 2",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    keywords="Spark PySpark TreasureData",
    extras_require={
        "spark": ['pyspark~={}'.format(pyspark_version)],
        "docs": ["sphinx>=2.2.0", "sphinx_rtd_theme>=0.4.3", "recommonmark"],
    },
)
