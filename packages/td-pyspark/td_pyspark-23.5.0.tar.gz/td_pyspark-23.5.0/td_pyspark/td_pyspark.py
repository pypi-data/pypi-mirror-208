import pathlib
from pyspark.sql import SQLContext, DataFrame


class TDSparkContextBuilder:
    """
    Util method to set TD-specific configuration and validation
    """
    ENDPOINTS = ["us", "jp", "eu01", "ap02"]

    @classmethod
    def default_jar_path(self):
        """Returns default td-spark jar path in the package

        :return: Default td-spark jar path inlcluded in td-pyspark package.
        :rtype: str

        :Example:

        >>> TDSparkContextBuilder.default_jar_path()
        '/usr/local/lib/python3.7/site-packages/td_pyspark/jars/td-spark-assembly.jar'
        """
        return str(pathlib.Path(__file__).parent / 'jars/td-spark-assembly.jar')

    def __init__(self, builder):
        """
        :param builder: A builder for `SparkSession`.
        :type builder: `pyspark.sql.SparkSession.Builder`
        """
        self.builder = builder

    def apikey(self, apikey):
        """Set apikey for td-spark

        :param apikey: apikey for TreasureData
        :type apikey: str
        :return: self
        """
        self.builder.config("spark.td.apikey", apikey)
        return self

    def api_endpoint(self, endpoint):
        """Set configuration of API host for TreasureData

        :param endpoint: API host name for TreasureData
        :type endpoint: str
        :return: self
        """
        self.builder.config("spark.td.api.host", endpoint)
        return self

    def presto_endpoint(self, endpoint):
        """Set configuration of Presto API host

        :param endpoint: Presto API host name for TreasureData
        :type endpoint: str
        :return: self
        """
        self.builder.config("spark.td.presto_api.host", endpoint)
        return self

    def plazma_endpoint(self, endpoint):
        """Set configuration for Plazma API host

        :param endpoint: Plazma API host name for TreasureData
        :type endpoint: str
        :return: self
        """
        self.builder.config("spark.td.plazma_api.host", endpoint)
        return self

    def site(self, siteName):
        """Set td-spark site to use

        :param siteName: "us", "jp", "eu01", or "ap02"
        :type siteName: str
        :return: self
        """
        if not siteName in TDSparkContextBuilder.ENDPOINTS:
            raise Exception("Unknown site name: {}. Use one of [{}]".format(siteName, ', '.join(TDSparkContextBuilder.ENDPOINTS)))
        self.builder.config("spark.td.site", siteName)
        return self

    def jars(self, jar_path):
        """Set spark.jars

        :param jar_path: Comma-separated list of jar file paths. Globs are allowed
        :type jar_path: str
        :return: self
        """
        self.builder.config("spark.jars", jar_path)
        return self

    def build(self):
        """Build TDSparkContext"""
        spark = self.builder.getOrCreate()
        return TDSparkContext(spark)


class TDSparkContext:
    """
    Treasure Data Spark Context
    """

    def __init__(self, spark, td=None):
        """
        :param spark: SparkSession already connected to Spark.
        :param td: Treasure Data Spark Context.
        :type spark: pyspark.sql.SparkSessio
        :type td: TDSparkContext, optional
        """
        self.spark = spark
        self.sqlContext = SQLContext(spark.sparkContext)
        self.sc = spark.sparkContext
        self.td = td if td else self.sc._jvm.com.treasuredata.spark.TDSparkContext.apply(self.sqlContext._ssql_ctx)
        self.context_db = "information_schema"

    def __to_df(self, sdf):
        return DataFrame(sdf, self.sqlContext)

    def df(self, table):
        """Load Treasure Data table into Spark DataFrame

        :param table: Table name of Treasure Data.
        :type table: str
        :return: Loaded table data.
        :rtype: pyspark.sql.DataFrame
        """
        sdf = self.td.df(table)
        return self.__to_df(sdf)

    def presto(self, sql, database=None):
        """Submit Presto Query

        :param sql: A SQL to be executed.
        :param database: Target database name.
        :type sql: str
        :type database: str, optional
        :return: SQL result
        :rtype: pyspark.sql.DataFrame

        :Example:

        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> spark = SparkSession.builder.master("local").getOrCreate()
        >>> td = TDSparkContext(spark)
        >>> sql = "select code, count(*) from sample_datasets.www_access group by 1"
        >>> q = td.presto(sql)
        >>> q.show()
        2019-06-13 20:09:13.245Z  info [TDPrestoJDBCRDD]  - (TDPrestoRelation.scala:106)
        Submit Presto query:
        select code, count(*) cnt from sample_datasets.www_access group by 1
        +----+----+
        |code| cnt|
        +----+----+
        | 200|4981|
        | 500|   2|
        | 404|  17|
        +----+----+
        """
        if database is None:
            database = self.context_db
        sdf = self.td.presto(sql, database)
        return self.__to_df(sdf)

    def execute_presto(self, sql, database=None):
        """Run non query statements (e.g., INSERT INTO, CREATE TABLE)

        :param sql: A SQL to be executed.
        :param database: Target database name.
        :type sql: str
        :type database: str, optional

        :Example:

        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession
        >>> import os
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        >>> td.execute_presto("CREATE TABLE IF NOT EXISTS A(time bigint, id varchar)")
        """
        if database is None:
            database = self.context_db
        self.td.executePresto(sql, database)

    def table(self, table):
        """Fetch TreasureData table

        :param table: Table name
        :type table: str
        :return: TD table data. `df()` method should be called to treat as
                 `spark.sql.DataFrame`.
        :rtype: TDTable

        :Example:

        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession
        >>> import os
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        >>> td.table("sample_datasets.www_access")
        <td_pyspark.td_pyspark.TDTable object at 0x10eedf240>
        """
        return TDTable(self.td.table(table), self.sc, self.sqlContext)

    def db(self, name):
        """Fetch TreasureData database

        :param name: Database name
        :type name: str
        :return: TD database data. `df()` method should be called to treat as
                 `spark.sql.DataFrame`.
        :rtype: TDDatabase

        :Example:

        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession
        >>> import os
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        >>> td.db("sample_datasets")
        <td_pyspark.td_pyspark.TDDatabase object at 0x10eedfa58>
        """
        return TDDatabase(self.td.db(name), self.sc, self.sqlContext)

    def set_log_level(self, log_level):
        """Set log level for Spark

        :param log_level: Log level for Spark process.
                          {"ALL", "DEBUG", "ERROR", "FATAL", "INFO", "OFF", "TRACE",
                          "WARN"}
        :type log_level: str

        :Example:

        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession
        >>> import os
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        >>> td.set_log_level("DEBUG")
        2019-09-06T18:19:12.398-0700  info [TDSparkContext] Setting the log level of com.treasuredata.spark to DEBUG - (TDSparkContext.scala:62)
        """
        self.td.setLogLevel(log_level)

    def use(self, name):
        """Change current database

        :param name: Target database name to be changed.
        :type name: str

        :Example:

        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession
        >>> import os
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        >>> td.use("mydb")
        2019-09-06T18:19:49.469-0700  info [TDSparkContext] Use mydb - (TDSparkContext.scala:150)
        """
        self.context_db = name
        self.td.use(name)

    def __new_td_context(self, td):
        return TDSparkContext(self.spark, td)

    def with_apikey(self, apikey):
        """Set an additional apikey

        :param apikey: apikey for TreasureData
        :type apikey: str

        :Example:

        >>> from td_pyspark import TDSparkContext
        >>> from pyspark.sql import SparkSession
        >>> spark = SparkSession.builder.master("local").getOrCreate()
        >>> td = TDSparkContext(spark)
        >>> td2 = td.with_apikey("key2")
        """
        return self.__new_td_context(self.td.withApiKey(apikey))

    def write(self, df, table_name, mode="error"):
        """Write a DataFrame as a TreasureData table

        :param df: Target DataFrame to be ingested to TreasureData.
        :param table_name: Target table name to be inserted.
        :param mode: Save mode same as Spark. {"error". "overwrite", "append", "ignore"}

                       - error: raise an exception.
                       - overwrite: drop the existing table, recreate it, and insert data.
                       - append: insert data. Create if does not exist.
                       - ignore: do nothing.

        :Example:

        >>> import os
        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession, Row
        >>> import pandas as pd
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        >>> df = td.spark.createDataFrame(pd.DataFrame({"name": ["Alice"], "age": [1]}))
        >>> td.write(df, "mydb.table1", "error")
        """
        writer = df.write.mode(mode).format("com.treasuredata.spark").option("table", table_name)
        if self.td.overrideConfig().nonEmpty():
            writer = writer.option("apikey", self.td.overrideConfig().get().apiKey())
        writer.save()

    def insert_into(self, df, table_name):
        """Insert a DataFrame into existing TreasureData table

        :param df: Target DataFrame to be ingested to TreasureData.
        :param table_name: Target table name to be inserted.
        :type df: pyspark.sql.DataFrame
        :type table_name: str

        :Example:

        >>> import os
        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession, Row
        >>> import pandas as pd
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        >>> df = td.spark.createDataFrame(pd.DataFrame({"name": ["Alice"], "age": [1]}))
        >>> td.insert_into(df, "mydb.table1")
        2019-09-09T10:57:37.558-0700  info [TDWriter] Uploading data to mydb.table1 (mode: Append) - (TDWriter.scala:66)
        2019-09-09T10:57:38.187-0700  info [TDWriter] [txx:8184891a] Starting a new transaction for updating mydb.table1 - (TDWriter.scala:95)
        2019-09-09T10:57:42.897-0700  info [TDWriter] [txx:8184891a] Finished uploading 1 partitions (1 records, size:132B) to mydb.table1 - (TDWriter.scala:132)
        """
        self.write(df, table_name, "append")

    def create_or_replace(self, df, table_name):
        """Create or replace a TreasureData table wity a DataFrame

        :param df: Target DataFrame to be ingested to TreasureData.
        :param table_name: Target table name to be ingested.
        :type df: pyspark.sql.DataFrame
        :type table_name: str

        :Example:

        >>> import os
        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession, Row
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        >>> df = td.spark.createDataFrame(pd.DataFrame({"name": ["Alice"], "age": [1]}))
        >>> td.create_or_replace(df, "mydb.table1")
        2019-09-09T10:57:56.381-0700  warn [DefaultSource] Dropping mydb.table1 (Overwrite mode) - (DefaultSource.scala:94)
        2019-09-09T10:57:56.923-0700  info [TDWriter] Uploading data to mydb.table1 (mode: Overwrite) - (TDWriter.scala:66)
        2019-09-09T10:57:57.106-0700  info [TDWriter] [txx:a69bce97] Starting a new transaction for updating aki.tds_test - (TDWriter.scala:95)
        2019-09-09T10:57:59.179-0700  info [TDWriter] [txx:a69bce97] Finished uploading 1 partitions (1 records, size:132B) to aki.tds_test - (TDWriter.scala:132)
        """
        self.write(df, table_name, "overwrite")

    def create_table_if_not_exists(self, table_name):
        """Create a table if not exists

        :param table_name: Target table name to be created.
        :type table_name: str

        :Example:

        >>> import os
        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession, Row
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        >>> td.create_table_if_not_exists(df, "mydb.table1")
        2019-09-09T13:43:41.142-0700  warn [TDTable] Creating table aki.tds_test if not exists - (TDTable.scala:67)
        """
        self.td.createTableIfNotExists(table_name)

    def drop_table_if_exists(self, table_name):
        """Drop a table if exists

        :param table_name: Target table name to be dropped.
        :type table_name: str

        :Example:

        >>> import os
        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession, Row
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        >>> td.drop_table_if_exists(df, "mydb.table1")
        """
        self.td.dropTableIfExists(table_name)

    def create_database_if_not_exists(self, db_name):
        """Create a database if not exits

        :param db_name: Target database name to be created.
        :type db_name: str

        :Example:

        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession, Row
        >>> import os
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        >>> td.create_database_if_not_exists(df, "mydb")
        """
        self.td.createDatabaseIfNotExists(db_name)

    def drop_database_if_exists(self, db_name):
        """Drop a database if exists

        :param db_name: Target database name to be dropped
        :type db_name: str

        :Example:

        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession, Row
        >>> import os
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        >>> td.drop_database_if_exists(df, "mydb")
        """
        self.td.dropDatabaseIfExists(db_name)

    def create_udp_l(self, table_name, long_column_name):
        """Create an User-Defined Partition Table partitioned by Long type column

        User-defined partitioning (UDP_) is useful if you know a column in the table
        that has unique identifiers (e.g., IDs, category values). This method is for
        creating a UDP table partitioned by Long type column.

        .. _UDP: https://docs.treasuredata.com/display/public/PD/Defining+Partitioning+for+Presto

        :param table_name: Target table name to be created as a UDP table.
        :param long_column_name: Partition column with Long (bigint) type column
        :type table_name: str
        :type long_column_name: str

        :Example:

        >>> import os
        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession, Row
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        >>> td.create_udp_l("mydb.departments", "dept_id")
        2019-09-09T10:43:20.913-0700  info [UDP]  - (UDP.scala:41)
        Preparing UDP table:
        -- td-spark: UDP creation
        create table if not exists "mydb"."departments" (
          time bigint,
          "dept_id" bigint
        )
        with (
          bucketed_on = array['dept_id'],
          bucket_count = 512
        )
        """
        self.td.createLongPartitionedTable(table_name, long_column_name)

    def create_udp_s(self, table_name, string_column_name):
        """Create an User-Defined Partition Table partitioned by string type column

        User-defined partitioning (UDP_) is useful if you know a column in the table
        that has unique identifiers (e.g., IDs, category values). This method is for
        creating a UDP table partitioned by string type column.

        .. _UDP: https://docs.treasuredata.com/display/public/PD/Defining+Partitioning+for+Presto

        :param table_name: Target table name to be created as a UDP table.
        :param string_column_name: Partition column with string type column

        :Example:

        >>> import os
        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession, Row
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        >>> td.create_udp_s("mydb.user_list", "id")
        2019-09-09T10:45:27.802-0700  info [UDP]  - (UDP.scala:41)
        Preparing UDP table:
        -- td-spark: UDP creation
        create table if not exists "mydb"."user_list" (
          time bigint,
          "id" varchar
        )
        with (
          bucketed_on = array['id'],
          bucket_count = 512
        )
        """
        self.td.createStringPartitionedTable(table_name, string_column_name)

    def swap_tables(self, table1, table2):
        """Swap table contents within the same database.

        :param table1:
        :param table2:

        :Example:

        >>> td.swap_tables("mydb.tbl1", "mydb.tbl2")
        """
        self.td.swapTables(table1, table2)


class TDDatabase:
    """
    An class represents a database on Treasure Data.
    """
    def __init__(self, db, sc, sqlContext):
        """
        :param db: A database object of td-spark
        :param sc: PySpark SparkContext
        :param sqlContext: PySpark SQLContext
        :type sc: pyspark.SparkContext
        :type sqlContext: pyspark.sql.SQLContext
        """
        self.db = db
        self.sc = sc
        self.sqlContext = sqlContext

    def exists(self):
        """Check database existence

        :return: Existence of the database
        :rtype: bool

        :Example:

        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession, Row
        >>> import os
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        >>> db1 = td.db("mydb")
        >>> db1.exists()
        True
        """
        return self.db.exists()

    def create_if_not_exists(self):
        """Create a database if not exists

        :Example:

        >>> import os
        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession, Row
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        >>> db1 = td.db("mydbtest")
        >>> db1.exists()
        False
        >>> db1.create_if_not_exists()
        2019-09-09T10:27:10.710-0700  warn [TDDatabase] Creating database mydbtest if not exists - (TDDatabase.scala:38)
        """
        self.db.createIfNotExists()

    def drop_if_exists(self):
        """Drop a database if exists

        :Example:

        >>> import os
        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession, Row
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        >>> db1 = td.db("mydbtest")
        >>> db1.exists()
        True
        >>> db1.drop_if_exists()
        2019-09-09T10:27:10.710-0700  warn [TDDatabase] Dropping database mydbtest if not exists - (TDDatabase.scala:38)
        """
        self.db.dropIfExists()

    def table(self, table):
        """Fetch the target TD table

        :param table: Target table name.
        :type table: str
        :return: Target TDTable
        :rtype: TDTable

        >>> import os
        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession, Row
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        >>> db1 = td.db("sample_datasets")
        >>> db1.table("www_access")
        <td_pyspark.td_pyspark.TDTable at 0x10a10c400>
        """
        return TDTable(self.db.table(table), self.sc, self.sqlContext)


class TDTable:
    """
    A class represents a table of Treasure Data
    """
    def __init__(self, table, sc, sqlContext):
        """
        :param table: A table object of td-spark
        :param sc: PySpark SparkContext
        :param sqlContext: PySpark SQLContext
        :type sc: pyspark.SparkContext
        :type sqlContext: pyspark.sql.SQLContext
        """
        self.table = table
        self.sc = sc
        self.sqlContext = sqlContext

    def __new_table(self, table):
        return TDTable(table, self.sc, self.sqlContext)

    def within(self, duration, timezone=None):
        """Filter a table with time range like TD_INTERVAL

        :param duration: A string to specify a target time range (e.g., "-1h"). For
                        detailed syntax, see also `TD_INTERVAL`_ function in Presto.
        :type duration: str
        :return: A TD table filtered by duration
        :rtype: TDTable

        .. _`TD_INTERVAL`: https://docs.treasuredata.com/display/public/PD/Supported+Presto+and+TD+Functions#SupportedPrestoandTDFunctions-TD_INTERVAL

        :Example:

        >>> import os
        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession, Row
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        # to read the last 1 hour range of data
        >>> td.table("tbl").within("-1h").df()
        # to read the last 1 day range of data
        >>> td.table("tbl").within("-1d").df()
        # to read the last 1 day range of data in JST timezone
        >>> td.table("tbl").within("-1d", "Asia/Tokyo")
        # to read the last day's data beginning from 7 days ago
        >>> td.table("tbl").within("-1d/-7d").df()
        # to set specific time range
        >>> td.table("sample_datasets.www_access").within("2014-10-04/2014-10-05").df()
        """
        tz = self.sc._jvm.java.time.ZoneId.of(timezone) if timezone else self.sc._jvm.java.time.ZoneOffset.UTC
        return self.__new_table(self.table.within(duration, tz))

    def drop_if_exists(self):
        """Drop a table if exists

        :Example:

        >>> import os
        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession, Row
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        >>> td.table("tbl").drop_if_exists()
        """
        self.table.dropIfExists()

    def create_if_not_exists(self):
        """Create a table if not exists

        :Example:

        >>> import os
        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession, Row
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        >>> td.table("tbl").create_if_not_exists()
        """
        self.table.createIfNotExists()

    def swap_table_with(self, target_table):
        """Swap the contents of tables

        :param target_table: A target table name. This target table must be in the same database.

        :Example:

        >>> td.table("mydb.tbl1").swap_table_with("tbl2")
        """
        self.table.swapTableWith(target_table)

    def exists(self):
        """Check the existence of the table

        :Example:

        >>> import os
        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession, Row
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        >>> td.table("tbl").exists()
        True
        """
        return self.table.exists()

    def within_unixtime_range(self, from_unixtime, to_unixtime):
        """Filter a table with unix time range

        This method filter the table [from_unixtime, to_unixtime).

        :param from_unixtime: Beginning unix time of the range, which is included.
        :param to_unixtime: End unix time of the range, which isn't included.
        :type from_unixtime: int
        :type to_unixtime: int
        :return: A filtered table by Unix time range

        :Example:

        >>> import os
        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession, Row
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        >>> t1 = td.table("sample_datasets.www_access")
        >>> t1.within_unixtime_range(1412320845, 1412321000)
        """
        return self.__new_table(self.table.withinUnixTimeRange(from_unixtime, to_unixtime))

    def within_utc_time_range(self, from_string, to_string):
        """Filter a table with time range of UTC Time Zone

        This method filter the table [from_string, to_string).

        :param from_string: Beginning of the range with `yyyy-MM-dd HH:mm:ss` format
                            e.g. "2014-10-03 09:12:00"
        :param to_string: End of the range with `yyyy-MM-dd HH:mm:ss` format.
        :type from_string: str
        :type to_string: str
        :return: A filtered table by UTC time range

        :Example:

        >>> import os
        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession, Row
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        >>> t1 = td.table("sample_datasets.www_access")
        >>> t1.within_utc_time_range("2014-10-03 09:12:00", "2014-10-03 09:13:00")
        """
        return self.within_time_range(from_string, to_string)

    def within_time_range(self, from_string, to_string, timezone=None):
        """Filter a table with time range with specified Time Zone

        This method filter the table [from_string, to_string).

        :param from_string: Beginning of the range with `yyyy-MM-dd HH:mm:ss` format
                            e.g. "2014-10-03 09:12:00"
        :param to_string: End of the range with `yyyy-MM-dd HH:mm:ss` format.
        :param timezone: Time Zone ID string which is passed to
                         ``java.time.ZoneId.of()`` e.g. "Asia/Tokyo"
        :type from_string: str
        :type to_string: str
        :type timezone: str
        :return: A filtered table by UTC time range

        :Example:

        >>> import os
        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession, Row
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        >>> t1 = td.table("sample_datasets.www_access")
        >>> t1.within_time_range("2014-10-03 18:12:00", "2014-10-03 18:13:00", "Asia/Tokyo")
        """

        tz = self.sc._jvm.java.time.ZoneId.of(timezone) if timezone else self.sc._jvm.java.time.ZoneOffset.UTC

        return self.__new_table(self.table.withinTimeRange(from_string, to_string, tz))

    def __to_pydf(self, sdf):
        return DataFrame(sdf, self.sqlContext)

    def df(self):
        """Convert table into a Spark DataFrame

        :return: A Spark DataFrame represents a TDTable
        :rtype: pyspark.sql.DataFrame

        :Example:

        >>> import os
        >>> from td_pyspark import TDSparkContext, TDSparkContextBuilder
        >>> from pyspark.sql import SparkSession, Row
        >>> builder = SparkSession.builder
        >>> td = TDSparkContextBuilder(builder).apikey(os.getenv("TD_API_KEY")). \
        ...      jars(TDSparkContextBuilder.default_jar_path()).build()
        >>> td.table("sample_datasets.www_access").df()
        """
        return self.__to_pydf(self.table.df())
