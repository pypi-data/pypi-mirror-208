td_pyspark
==

[Treasure Data](https://treasuredata.com) extension for using [pyspark](https://spark.apache.org/docs/latest/api/python/index.html).

```sh
$ pip install td-pyspark
```

This document is only for internal developers, see also [README_public.md](README_public.md) for further usage.

# For Developers

Running pyspark with td_pyspark:

```bash
$ ${SPARK_HOME}/bin/spark-submit --master "local[4]"  --driver-class-path td-spark-assembly.jar  --properties-file=td-spark.conf --py-files td_pyspark.py your_app.py
```

## How To Publish td_pyspark 

td_pyspark will be automatically released to PyPI with GitHub Actions when a new git tag is added. If you need to manually install td_pyspark, read the following instructions:


### Prerequisites 

[Twine](https://pypi.org/project/twine/) is a secure utility to publish the python package. It's commonly used to publish Python package to PyPI.
First you need to install the package in advance.

```bash
$ pip install twine
```

Having the configuration file for PyPI credential may be useful.

```
$ cat << 'EOF' > ~/.pypirc 
[distutils]
index-servers =
  pypi
  testpypi

[pypi]
repository=https://upload.pypi.org/legacy/
username=<your_username>
password=<your_password>

[testpypi]
repository=https://test.pypi.org/legacy/
username=<your_username>

password=<your_password>
EOF
```

The credentials for TD account of [pypi.org](https://pypi.org/user/treasure_data/) and [test.pypi.org](https://test.pypi.org/user/treasure_data/) is stored in the [Box note](https://treasure-data.app.box.com/notes/560859904521).

### Build Package

Build the package in the raw source code and wheel format.

```
$ make package
```

To create an early-access (ea) version of td-pyspark, set PROJECT_NAME and SPARK_VERSION:
```
$ PROJECT_NAME=td_pyspark_ea SPARK_VERSION=3.0.1 make package
```

If you need to force setting a td-pyspark version, set VERSION env as well. For example:
```
$ VERSION=20.6.1 PROJECT_NAME=td_pyspark_ea SPARK_VERSION=3.0.1 make package
```

### Publish Package

Upload the package to the test repository first.

```
$ make clean upload-test
```

If you do not find anything wrong in the test repository (
https://test.pypi.org/project/td-pyspark/ or
https://test.pypi.org/project/td-pyspark-ea/), then it's time to publish the package.


```
$ make clean upload
```

- Release versions: https://pypi.org/project/td-pyspark/
- Early access versions: https://pypi.org/project/td-pyspark-ea/


To upload an early access version of td-pyspark for a specific version of Spark (e.g., 3.0.1), use the following commands:
```
$ PROJECT_NAME=td_pyspark_ea SPARK_VERSION=3.0.1 make upload-test
$ PROJECT_NAME=td_pyspark_ea SPARK_VERSION=3.0.1 make upload
```

## Customize API endpoints


Use `TDSparkContextBuilder` to specify different API endpoints (e.g., development API):
```python
import td_pyspark
from pyspark.sql import SparkSession

builder = SparkSession\
    .builder\
    .appName("td-pyspark-app")
    
td = td_pyspark.TDSparkContextBuilder(builder)\
    .apikey("XXXXXXXXXXXXXX")\
    .api_endpoint("api.treasuredata.com")\
    .build()

# Read the table data within -1d (yesterday) range as DataFrame
df = td.table("sample_datasets.www_access")\
    .within("-1d")\
    .df()
    
df.show()
```

## Build documentation

You need to install Sphinx and it's extensions for documentation as follows:

```sh
pip install td-pyspark[docs]
```

or install dependencies in the td_pyspark directory after clone the repository.

```sh
pip install -e .[docs]
```

After installation of dependent Python packages, you can build the document as:

```sh
make doc
```

This command will generate the document under `docs/_build/html` directory.
