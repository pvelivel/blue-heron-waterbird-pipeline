import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from awsglue.job import Job
from pyspark.sql.functions import col, trim, upper, length, when

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# S3 paths
input_path = "s3://blue-heron-waterbird-data/cleaned/state_filtered/valid/"
aou_path = "s3://blue-heron-waterbird-data/reference/AOU_Codes.csv"
colonial_path = "s3://blue-heron-waterbird-data/reference/species_list.csv"
output_path = "s3://blue-heron-waterbird-data/cleaned/species_filtered/"

# Step 1: Load and clean input
df = spark.read.parquet(input_path)
if "Comments" in df.columns:
    df = df.drop("Comments")

# Normalize 'species' column
df = df.withColumn("species", upper(trim(col("species"))))
df = df.withColumn("AOU_CODE", when(length(col("species")) == 4, col("species")))
df = df.withColumn("COMMON_NAME", when(length(col("species")) > 4, col("species")))

# Step 2: Load and clean AOU mapping
df_aou = spark.read.option("header", True).csv(aou_path)
df_aou = df_aou.select("Spec", "COMMONNAME") \
    .withColumnRenamed("Spec", "AOU_CODE") \
    .withColumnRenamed("COMMONNAME", "AOU_COMMON_NAME")
df_aou = df_aou.withColumn("AOU_CODE", upper(trim(col("AOU_CODE")))) \
               .withColumn("AOU_COMMON_NAME", upper(trim(col("AOU_COMMON_NAME"))))

# Step 3: Join to fill missing common names
df_main = df.join(df_aou, on="AOU_CODE", how="left")
df_main = df_main.withColumn("COMMON_NAME",
                             when(col("COMMON_NAME").isNull(), col("AOU_COMMON_NAME"))
                             .otherwise(col("COMMON_NAME"))) \
                 .drop("AOU_COMMON_NAME")

# Step 4: Load and clean colonial species list
df_colonial = spark.read.option("header", True).csv(colonial_path)
df_colonial = df_colonial.withColumnRenamed("COMMON NAME", "COMMON_NAME")
df_colonial = df_colonial.withColumn("COMMON_NAME", upper(trim(col("COMMON_NAME"))))

# Step 5: Filter colonial vs non-colonial species
df_valid = df_main.join(df_colonial, on="COMMON_NAME", how="inner")
df_removed = df_main.join(df_colonial, on="COMMON_NAME", how="left_anti")

# Step 6: Final cleanup
if "Comments" in df_valid.columns:
    df_valid = df_valid.drop("Comments")
if "Comments" in df_removed.columns:
    df_removed = df_removed.drop("Comments")

# Step 7: Write to S3
df_valid.write.mode("overwrite").parquet(output_path + "valid/")
df_removed.write.mode("overwrite").parquet(output_path + "removed/")

job.commit()