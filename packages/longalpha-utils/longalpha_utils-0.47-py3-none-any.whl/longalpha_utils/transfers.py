import os
import tempfile
from io import BytesIO
from typing import List, Optional, Dict, Any, Union
import pandas as pd
from minio import Minio
from pyspark.conf import SparkConf
from pyspark.sql import SparkSession, DataFrame
from sqlalchemy import Engine
from sqlalchemy import create_engine
from sqlalchemy import text
from minio.error import S3Error
from datetime import date, timedelta
from pyspark.sql.utils import AnalysisException
from longalpha_utils.utils import  multi_union_by_name
def init_spark(
    spark_executor_memory: str = "30g",
    spark_driver_memory: str = "90g",
    minio_endpoint: Optional[str] = None,
    minio_access_key: Optional[str] = None,
    minio_secret_key: Optional[str] = None,
) -> SparkSession:
    """
    get a spark instance.

    if connect_psql is True, then we will connect to psql.
    if minio_endpoint is not None, then we will connect to minio.
    if both are None, then we will connect to local spark.

    Note that we are not downloading jars here. We use spark.jars.packages to download jars.

    Args:
        minio_endpoint: minio_endpoint
        minio_access_key:  minio_access_key
        minio_secret_key:  minio_secret_key
        spark_executor_memory: size of spark_executor_memory
        spark_driver_memory: size of spark_driver_memory
    Returns:

    """
    jars = [
        "org.postgresql:postgresql:42.5.2",
        "org.apache.hadoop:hadoop-aws:3.3.2",
        "com.amazonaws:aws-java-sdk-bundle:1.12.405",
    ]

    spark_conf = (
        SparkConf()
        .set("spark.executor.memory", spark_executor_memory)
        .set("spark.driver.memory", spark_driver_memory)
        .set("spark.sql.execution.arrow.pyspark.enabled", "true")
        .set("spark.ui.port", "4043")
        .set(
            "spark.jars.packages", ",".join(jars)
        )  # if you set park.jars.packages more than once, only the last one will be used.
        .set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .set("spark.hadoop.fs.s3a.path.style.access ", "true")
    )
    spark = SparkSession.builder.config(conf=spark_conf).getOrCreate()

    if minio_endpoint is not None:
        spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.endpoint", minio_endpoint)
        spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.access.key", minio_access_key)
        spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.secret.key", minio_secret_key)
        spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.connection.ssl.enabled", "false")

    return spark

class MinioWrapper:
    def __init__(self, minio_url, minio_access_key, minio_secret_key):
        self.minio_client = Minio(
            endpoint=minio_url,
            access_key=minio_access_key,
            secret_key=minio_secret_key,
            secure=False,
        )

    def object_exists(self, bucket_name: str, object_name: str) -> bool:
        """
        check if an object exists in the bucket
        Args:
            bucket_name: Minio bucket_name
            object_name: object name in the minio bucket

        Returns: True if the object exists, False otherwise

        """
        try:
            self.minio_client.stat_object(bucket_name, object_name)
            return True
        except S3Error as e:
            if e.code == "NoSuchKey":
                return False

    def fput(
        self,
        file_path,
        bucket_name: str,
        object_name: str,
    ) -> None:
        """
        put a file to s3
        Args:
            file_path: path to the file
            bucket_name: Minio bucket_name
            object_name: object name in the minio bucket

        Returns:

        """
        self.minio_client.fput_object(bucket_name=bucket_name, object_name=object_name, file_path=file_path)

    def put(self, dataframe: pd.DataFrame, bucket_name: str, object_name: str, index=False) -> None:
        """
        put a pandas frame to parquet in s3

        Args:
            dataframe: a pandas dataframe
            bucket_name: Minio bucket_name
            object_name: object name in the minio bucket
            index: whether to save the index of the dataframe, only used for parquet


        Returns:

        """
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "file.parquet")
            dataframe.to_parquet(path, index=index)

            self.fput(file_path=path, bucket_name=bucket_name, object_name=object_name)

    def fget(self, file_path: str, bucket_name: str, object_name: str):
        self.minio_client.fget_object(bucket_name=bucket_name, object_name=object_name, file_path=file_path)

    def get(
        self,
        bucket_name: str,
        object_name: str,
    ) -> pd.DataFrame:
        """
        get a parquet from s3 and read it into pandas dataframe
        Args:
            bucket_name: Minio bucket_name
            object_name: path + file_name

        Returns: A pandas dataframe

        """
        file = self.minio_client.get_object(
            bucket_name,
            object_name,
        )
        res = pd.read_parquet(BytesIO(file.data))
        file.close()
        file.release_conn()
        return res

    def get_latest(self, bucket_name: str) -> pd.DataFrame:
        """
        get the latest parquet file and read it into pandas. Note that this does not include files in the
        sub-folders of the bucket. To do this, we need to recursively list all the files in the bucket.
        Args:
            bucket_name: bucket_name: Minio bucket_name

        Returns: A pandas dataframe

        """
        objects = [i for i in self.minio_client.list_objects(bucket_name)]
        time_obj = {obj.last_modified: obj for obj in objects}
        latest_time = max([key for key in time_obj.keys() if key is not None])
        latest_obj = time_obj[latest_time]
        return self.get(bucket_name=bucket_name, object_name=latest_obj.object_name)

    def list(self, bucket_name: str) -> List[str]:
        return [i.object_name for i in self.minio_client.list_objects(bucket_name)]




def get_s3_data_spark(
        spark: SparkSession, start_date: date, end_date: date, bucket: str, subfolder: str,
) -> Union[DataFrame, None]:
    """
    Get options data from minio
    Args:
        spark: spark session
        start_date: start date to get options data for
        end_date: end date to get options data for

    Returns: options data if exists, None otherwise.
    Note returned options data is in wide format with calls and puts on the same row

    """
    options = []
    while start_date <= end_date:
        file_s3_path = "s3a://" +os.path.join(bucket, f"{subfolder}/{start_date}.parquet")
        try:
            option = spark.read.parquet(file_s3_path)
            options.append(option)
        except AnalysisException:
            print(f"Options data for {start_date} does not exist.")
        start_date += timedelta(days=1)
    if len(options) == 0:
        return None
    unioned_options = multi_union_by_name(options)
    return unioned_options



def spark_read_psql(
    spark: SparkSession, psql_url: str, psql_db: str, psql_table: str, psql_usr: str, psql_pwd: str
) -> DataFrame:
    """
    use spark to read psql
    Args:
        spark: spark instance. Must be created with support for psql.
        psql_url: url of psql
        psql_db: database name
        psql_table: table name
        psql_usr: username of psql
        psql_pwd: password of psql

    Returns: a pyspark dataframe

    """
    return (
        spark.read.format("jdbc")
        .option("url", f"jdbc:postgresql://{psql_url}/{psql_db}")
        .option("dbtable", psql_table)
        .option("user", psql_usr)
        .option("password", psql_pwd)
        .option("driver", "org.postgresql.Driver")
        .load()
    )


def df_to_psql(
    df: pd.DataFrame,
    table_name: str,
    index=False,
    dtype: Optional[Dict[str, Any]] = None,
    if_exists: str = "append",
    engine: Optional[Engine] = None,
    user_name: Optional[str] = None,
    password: Optional[str] = None,
    host_with_port: Optional[str] = None,
    db_name: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """
    write a pandas dataframe to psql
    Args:
        df: pandas dataframe
        table_name: table name to write to psql
        index: whether to write index to psql
        dtype: data type of column. If a dictionary is used, the keys should be the column names and the values
        should be the SQLAlchemy types or strings for the sqlite3 legacy mode
        if_exists: {‘fail’, ‘replace’, ‘append’}, default ‘append’. How to behave if the table already exists.
        engine: sqlalchemy engine. If not None, then we will use this engine to write to psql.
        user_name: username of psql
        password: password of psql
        host_with_port: host_with_port of psql
        db_name: database name of psql to write to
        kwargs: additional keyword argument passed to DataFrame.to_sql

    Returns: None

    """
    if engine is not None and user_name is not None:
        raise ValueError("engine and user_name cannot be both not None")
    if engine is None and user_name is None:
        raise ValueError("engine and user_name cannot be both None")
    if engine is None:
        engine = create_engine(f"postgresql://{user_name}:{password}@{host_with_port}/{db_name}")
    df.to_sql(table_name, con=engine, index=index, if_exists=if_exists, dtype=dtype, **kwargs)


def df_from_psql(
    sql: str,
    engine: Optional[Engine] = None,
    user_name: Optional[str] = None,
    password: Optional[str] = None,
    host_with_port: Optional[str] = None,
    db_name: Optional[str] = None,
    **kwargs: Any,
) -> pd.DataFrame:
    """
    read a pandas dataframe from psql
    Args:
        sql: sql query
        engine: sqlalchemy engine. If not None, then we will use this engine to write to psql.
        user_name:  username of psql
        password: password of psql
        host_with_port: host_with_port of psql
        db_name: database name of psql to write to
        **kwargs: additional keyword argument passed to pd.read_sql

    Returns:

    """
    if engine is not None and user_name is not None:
        raise ValueError("engine and user_name cannot be both not None")
    if engine is None and user_name is None:
        raise ValueError("engine and user_name cannot be both None")
    if engine is None:
        engine = create_engine(f"postgresql://{user_name}:{password}@{host_with_port}/{db_name}")
    query = text(sql)
    return pd.read_sql(sql=query, con=engine.connect(), **kwargs)
