# Databricks notebook source
# Specify the catalog and schema to use. You must have USE_CATALOG privilege on the catalog and USE_SCHEMA and CREATE_TABLE privileges on the schema.
# Change the catalog and schema here if necessary.
# COMMAND ----------
dbutils.widgets.text("catalog", "main")
dbutils.widgets.text("schema_name", "default")
dbutils.widgets.text("source_data_path", "dbfs:/databricks-datasets/wikipedia-datasets/data-001/en_wikipedia/articles-only-parquet")
dbutils.widgets.text("source_table_name","wiki_articles_demo")
dbutils.widgets.text("chunk_size","500")
# COMMAND ----------
catalog_name = dbutils.widgets.get("catalog")
schema_name = dbutils.widgets.get("schema_name")
source_table_name = dbutils.widgets.get("source_table_name")
source_data_path = dbutils.widgets.get("source_data_path")
max_chunk_tokens = int(dbutils.widgets.get("chunk_size"))

# COMMAND ----------
import tiktoken
import pandas as pd
from vector_search.etl_utils import chunk_text
# COMMAND ----------
import os
source_table_fullname = f"{catalog_name}.{schema_name}.{source_table_name}"
source_df = spark.read.parquet(source_data_path).limit(5)
# The GTE model has been trained on a max context lenth of 8192 tokens.
# COMMAND ----------
encoding = tiktoken.get_encoding("cl100k_base")

# Process the data and store in a new list
pandas_df = source_df.toPandas()
processed_data = []
for index, row in pandas_df.iterrows():
    text_chunks = chunk_text(row['text'], max_chunk_tokens, encoding)
    chunk_no = 0
    for chunk in text_chunks:
        row_data = row.to_dict()
        
        # replace the id column with a new unique chunk id
        # and the text column with the text chunk
        row_data['id'] = f"{row['id']}_{chunk_no}"
        row_data['text'] = chunk
        
        processed_data.append(row_data)
        chunk_no += 1

chunked_pandas_df = pd.DataFrame(processed_data)
chunked_spark_df = spark.createDataFrame(chunked_pandas_df)
# COMMAND ----------
# Write the chunked DataFrame to a Delta table
spark.sql(f"DROP TABLE IF EXISTS {source_table_fullname}")
chunked_spark_df.write.format("delta") \
    .option("delta.enableChangeDataFeed", "true") \
    .saveAsTable(source_table_fullname)