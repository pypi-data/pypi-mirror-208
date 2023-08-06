import json
import logging
from datetime import datetime, timedelta
import jwt
from pymongo import MongoClient
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count
from pyspark.sql.types import StringType, StructType, StructField, TimestampType, IntegerType
from pyspark.sql import functions as F
import certifi
from pymongo.server_api import ServerApi
from pyspark.sql.functions import col


class materialize:
    def __init__(self, mongo_connection, aggregation_date, groupby_attr, groupby_value, token, schema, sparksql, partition_column=None):
        self.mongo_connection = mongo_connection
        self.aggregation_date = datetime.strptime(aggregation_date, "%Y-%m-%d %H:%M:%S")
        self.groupby = groupby_value
        self.groupby_attr = groupby_attr
        self.token = token
        self.schema = schema
        self.sparksql = sparksql
        self.partition_column = partition_column

        self.spark = SparkSession.builder \
            .appName("IncrementalAggregation") \
            .master("local[*]") \
            .getOrCreate()
        self.spark.sparkContext.setLogLevel("ERROR")

    def read_data_and_aggregate(self):


        # authenticate token
        mongo_client = MongoClient(self.mongo_connection['uri'], server_api=ServerApi('1'), tlsCAFile=certifi.where())
        mongo_db = mongo_client[self.mongo_connection['database']]
        mongo_db_featurizer = mongo_client['featurizer']
        users_collection = mongo_db_featurizer["users"]
        SECRET_KEY = "features"  # Change this to your desired secret key
        TOKEN_EXPIRATION = 3600  # Token expiration in seconds (1 hour)

        try:
            payload = jwt.decode(self.token, SECRET_KEY, algorithms=["HS256"])
            user_id: str = payload.get("user_id")
            if user_id is None:
                print("User not found")
                return ("Invalid token")
            print("Authenticated user: " + user_id)
            user = users_collection.find_one({"userid": user_id})
            if user is None:
                print("User not found")
                return ("Invalid token")
        except Exception as e:
            print(e)
            return ("Invalid token")

        raw_data_collection = mongo_db[self.mongo_connection['rawdata']]
        aggregated_data_collection = mongo_db[self.mongo_connection['collection']]

        raw_data = raw_data_collection.find()
        raw_data_list = [doc for doc in raw_data]
        df = self.spark.createDataFrame(raw_data_list, self.schema)

        # Apply partitioning if the partition_column is specified
        if self.partition_column:
            print("Partitioning the DataFrame based on the column: " + self.partition_column)
            raw_data_collection.create_index(self.partition_column)
            raw_data_collection.create_index(self.groupby_attr)
            df = df.repartition(col(self.partition_column))

        # Filter the DataFrame based on the given device_id
        df = df.filter(col(self.groupby_attr) == self.groupby)
        start_time = self.aggregation_date
        df = df.filter((col(self.groupby_attr) == self.groupby) & (col("timestamp") < start_time.timestamp()))
        df = df.withColumn("timestamp_unix", F.col("timestamp").cast("bigint"))
        df.createOrReplaceTempView("temp_table")

        # Define empty schema for DataFrame
        schema = StructType([
            StructField(self.groupby_attr, StringType(), True)
        ])
        # Create empty DataFrame
        result_df = self.spark.createDataFrame([], schema)

        # Execute the dynamic Spark SQL
        for sql in self.sparksql:
            sql_base = sql.replace("{"+ self.groupby_attr + "}", str(self.groupby))
            hour = int(sql.split("_")[2])
            sql_with_timestamp = sql_base.replace("{timestamp}", str(int((start_time - timedelta(hours=hour)).timestamp())))
            sql_with_timestamp_base = sql_with_timestamp.replace("{timestamp_base}", str(int((start_time).timestamp())))
            c_count = self.spark.sql(sql_with_timestamp_base)
            result_df = result_df.join(c_count, self.groupby_attr, "full") \
                .select(result_df.columns + [col for col in c_count.columns if col not in result_df.columns])

        if result_df.isEmpty():
            json_aggregated_data = "{'error': 'No data found'}"
        else:
            json_aggregated_data = result_df.toJSON().collect()[0]

        if json_aggregated_data is not None:
            aggregated_data_collection.update_one(
                {"date": start_time, "aggregated_key": self.groupby},
                {"$set": {"aggregated_data": json_aggregated_data}},
                upsert=True
            )
        else:
            logging.error("Serialized aggregated data is None, skipping update")

        return json_aggregated_data


