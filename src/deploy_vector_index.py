# Databricks notebook source
# Default notebook
## This default notebook is executed using Databricks Workflows as defined in resources/vector_search_job.yml
# COMMAND ----------

# # DBTITLE 1,Initialize widgets
dbutils.widgets.text("catalog", "main")
dbutils.widgets.text("schema_name", "default")
dbutils.widgets.text("source_table_name","wiki_articles_demo")
dbutils.widgets.text("endpoint_name", "vector_search_demo_endpoint")
dbutils.widgets.text("embedding_model_endpoint", "databricks-bge-large-en")
dbutils.widgets.text("pipeline_type","TRIGGERED")
dbutils.widgets.text("primary_key", "id")
dbutils.widgets.text("embedding_source_column", "text")
# dbutils.widgets.text("index_name", "wiki_articles_cw_index")

catalog_name = dbutils.widgets.get("catalog")
schema_name = dbutils.widgets.get("schema_name")
source_table_name = dbutils.widgets.get("source_table_name")
endpoint_name = dbutils.widgets.get("endpoint_name")
embedding_model_endpoint = dbutils.widgets.get("embedding_model_endpoint")
pipeline_type = dbutils.widgets.get("pipeline_type")
primary_key = dbutils.widgets.get("primary_key")
embedding_source_column = dbutils.widgets.get("embedding_source_column")
# index_name = dbutils.widgets.get("index_name")

full_table_name = f"{catalog_name}.{schema_name}.{source_table_name}"
index_name = f"{source_table_name}_bge_index"
full_index_name = f"{catalog_name}.{schema_name}.{index_name}"

spark.sql(f"USE CATALOG {catalog_name}")
spark.sql(f"USE SCHEMA {schema_name}")

print(f"using catalog {catalog_name}")
print(f"using schema {schema_name}")
print(f"using table {source_table_name}")
print(f"using embedding model endpoint {embedding_model_endpoint}")
print(f"using endpoint {endpoint_name}")
print(f"using index name {index_name}")
print(f"using full table name {full_table_name}")
print(f"using full index name {full_index_name}")
# COMMAND ----------

from databricks.vector_search.client import VectorSearchClient
from vector_search.vs_utils import (
    vector_search_endpoint_exists,
    vector_index_exists,
    create_vector_index,
    sync_vector_index)

vsc = VectorSearchClient(disable_notice=True)

if vector_search_endpoint_exists(vsc, endpoint_name):
    print(f"{endpoint_name} already exists")
else:
    vsc.create_endpoint(endpoint_name)
    print(f"{endpoint_name} created")


# DBTITLE 1,Ensure vector index exists
if vector_index_exists(vsc, endpoint_name, full_index_name):
    print(f"{index_name} already exists")
    # For Triggered mode index
    print(f"Sync updates {index_name}") 
    sync_vector_index(vsc, endpoint_name, full_index_name)
    print(f"{index_name} updated") 
else:
    print(f"Create index {index_name}")
    create_vector_index(vsc, 
                        full_table_name, 
                        endpoint_name, 
                        full_index_name, 
                        embedding_model_endpoint, 
                        pipeline_type,
                        primary_key,
                        embedding_source_column)
    print(f"{index_name} created")