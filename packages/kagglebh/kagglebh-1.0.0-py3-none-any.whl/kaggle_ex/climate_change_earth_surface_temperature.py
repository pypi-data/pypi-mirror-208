import pyspark
import os

from pyspark.sql.functions import col, max
from zipfile import ZipFile


# this module uses kaggle api to get the dataset
# first we need to manually create kaggle api token and store it 
# in this exercise it is stored in kaggle.json in dbfs : dbfs:/FileStore/kaggle.json - as we don't have access to the Key Vault
# in real life project secrets should be stored in eg. Azure Key Vault

spark = pyspark.sql.SparkSession.builder.appName("kaggle_app").getOrCreate()

KAGGLE_KEY      = spark.read.json("dbfs:/FileStore/kaggle.json").select("key").collect()[0][0]
KAGGLE_USERNAME = spark.read.json("dbfs:/FileStore/kaggle.json").select("username").collect()[0][0]

# function to authenticate kaggle api

def kaggle_auth(KAGGLE_USERNAME, KAGGLE_KEY):
  os.environ["KAGGLE_USERNAME"] = KAGGLE_USERNAME
  os.environ["KAGGLE_KEY"] = KAGGLE_KEY
  from kaggle.api.kaggle_api_extended import KaggleApi
  api = KaggleApi()
  api.authenticate()
  return api

# function to read csv file saved in a driver vm

def read_csv(path):
  return(spark.read.format("csv").option("header", True).load(path)
  )

# function to 
# 1 upload from kaggle, 
# 2 unzip it 
# 3 read csv file saved in a driver vm - in real life project data would be stored in some cloud storage account
# 4 transform input data
# 5 save the data as parquet in a target destination

def transform_and_write(KAGGLE_FILE_PATH, KAGGLE_FILE_NAME, TARGET_PATH):
  api = kaggle_auth(KAGGLE_USERNAME, KAGGLE_KEY)
  api.dataset_download_file(KAGGLE_FILE_PATH, f"{KAGGLE_FILE_NAME}.csv")
  with ZipFile("GlobalLandTemperaturesByState.csv.zip", 'r') as zObject:
      zObject.extractall()
  df = read_csv(f"file:/databricks/driver/{KAGGLE_FILE_NAME}.csv")
  df_agg = df.groupBy("Country", "State").agg(max(col("AverageTemperature")).alias("MaxAverageTemperature"))
  df_agg.write.format("parquet").mode("overwrite").save(TARGET_PATH)