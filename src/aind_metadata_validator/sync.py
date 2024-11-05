"""Main entrypoint"""

from aind_metadata_validator.metadata_validator import validate_metadata
from aind_data_access_api.document_db import MetadataDbClient
# from aind_data_access_api.rds_tables import RDSCredentials
import pandas as pd
import os
import logging

API_GATEWAY_HOST = os.getenv("API_GATEWAY_HOST", "api.allenneuraldynamics-test.org")
DATABASE = os.getenv("DATABASE", "metadata_index")
COLLECTION = os.getenv("COLLECTION", "data_assets")

client = MetadataDbClient(
    host=API_GATEWAY_HOST,
    database=DATABASE,
    collection=COLLECTION,
)

if __name__ == "__main__":
    logging.info("(METADATA VALIDATOR): Starting run")

    # rds_credentials = RDSCredentials(aws_secrets_name=REDSHIFT_SECRETS_NAME)
    response = client.retrieve_docdb_records(
        filter_query={},
        limit=0,
        paginate_batch_size=500,
    )

    logging.info(f"(METADATA VALIDATOR): Retrieved {len(response)} records")

    results = []
    for record in response:
        results.append(validate_metadata(record))

    pd.DataFrame(results).to_csv("validation_results.csv", index=False)