import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from awsglue.job import Job
from pyspark.sql.functions import col, when, trim, upper, initcap

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# S3 paths
input_path = "s3://blue-heron-waterbird-data/cleaned/species_filtered/valid/"
output_path = "s3://blue-heron-waterbird-data/cleaned/population_cleaned/valid/"

# Step 1: Load cleaned species data
df = spark.read.parquet(input_path)

# Step 2: Fill PopulationEstimate
df = df.withColumn("PopulationEstimate",
    when(col("PopulationEstimate").isNotNull(), col("PopulationEstimate"))
    .when(col("CorrectedCount").isNotNull(), col("CorrectedCount"))
    .when(col("UncorrectedCount").isNotNull(), col("UncorrectedCount"))
    .otherwise(None)
)

# Step 3: Standardize SurveyMethod and DataQuality
df = df.withColumn("SurveyMethod", initcap(trim(col("SurveyMethod")))) \
       .withColumn("DataQuality", upper(trim(col("DataQuality"))))

# Step 4: Write output
df.write.mode("overwrite").parquet(output_path)

job.commit()
