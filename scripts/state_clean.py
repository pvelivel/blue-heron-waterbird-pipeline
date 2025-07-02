import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql.functions import col, upper
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# S3 paths
main_data_path = "s3://blue-heron-waterbird-data/raw/usgs_cwbData_variables.csv"
state_list_path = "s3://blue-heron-waterbird-data/reference/state_province_list.csv"
output_path = "s3://blue-heron-waterbird-data/cleaned/state_filtered/"

# Read CSV files
df_main = spark.read.option("header", True).csv(main_data_path)
df_states = spark.read.option("header", True).csv(state_list_path)

from pyspark.sql.functions import when

df_states = df_states.dropna(subset=["ABB"]) \
    .withColumn("ABB", when(col("ABB") == "PEI", "PE").otherwise(col("ABB")))


# Uppercase and normalize main data
df_main = df_main.withColumn("State", upper(col("State")))

# Collect valid states into Python list
valid_states = [row["ABB"] for row in df_states.select("ABB").collect()]

# Filter main data by valid states
df_filtered = df_main.filter(col("State").isin(valid_states))
df_removed = df_main.filter(~col("State").isin(valid_states))

# Write results as Parquet
df_filtered.write.mode("overwrite").parquet(output_path + "valid/")
df_removed.write.mode("overwrite").parquet(output_path + "removed/")

job.commit()