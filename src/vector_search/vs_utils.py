from databricks.vector_search.client import VectorSearchClient

def vector_search_endpoint_exists(vsc: VectorSearchClient, endpoint_name: str) -> bool:
    """Check if the given endpoint already exists."""
    response = vsc.list_endpoints()
    endpoints = response["endpoints"]

    # Check if our endpoint already exists (we assume the name is a match if it exists)
    for endpoint in endpoints:
        if endpoint_name == endpoint["name"]:
            return True
        
    return False


def vector_index_exists(vsc: VectorSearchClient, endpoint_name: str, index_name: str) -> bool:
    """Check if the index already exists on the endpoint."""
    response = vsc.list_indexes(endpoint_name)
    vector_indexes = response["vector_indexes"]

    # Check if our index already exists (we assume the name is a match if it exists)
    for index in vector_indexes:
        if index_name == index["name"]:
            return True
        
    return False


def create_vector_index(
    vsc: VectorSearchClient,
    table_name: str,
    endpoint_name: str,
    index_name: str,
    embedding_model_endpoint: str,
    pipeline_type: str,
    primary_key: str,
    embedding_source_column: str
) -> None:
    """Create a vector search index based on the source table."""
    try: 
        vsc.create_delta_sync_index_and_wait(
            endpoint_name=endpoint_name,
            index_name=index_name,
            source_table_name=table_name,
            pipeline_type="TRIGGERED",
            primary_key="id",
            embedding_source_column="text",
            embedding_model_endpoint_name=embedding_model_endpoint
            )
    except Exception as e:
        if "already exists" in str(e):
            pass
        else:
            raise e

def sync_vector_index(
    vsc: VectorSearchClient,
    endpoint_name: str,
    index_name: str
) -> None:
    """Sync a vector search index with delta sync"""
    try:
        index = vsc.get_index(endpoint_name, index_name)
        index.sync()
        index.wait_until_ready()
    except Exception as e:
        raise e