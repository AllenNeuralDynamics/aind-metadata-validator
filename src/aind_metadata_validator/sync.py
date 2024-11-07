"""Main entrypoint"""

from aind_metadata_validator.metadata_validator import validate_metadata
from aind_data_access_api.document_db import MetadataDbClient
from aind_data_access_api.rds_tables import RDSCredentials
from aind_data_access_api.rds_tables import Client
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

DEV_OR_PROD = "dev" if "test" in API_GATEWAY_HOST else "prod"
REDSHIFT_SECRETS = f"/aind/{DEV_OR_PROD}/redshift/credentials/readwrite"
RDS_TABLE_NAME = f"metadata_status_{DEV_OR_PROD}"

CHUNK_SIZE = 1000

rds_client = Client(
            credentials=RDSCredentials(
               aws_secrets_name=REDSHIFT_SECRETS
            ),
      )

if __name__ == "__main__":
    logging.info("(METADATA VALIDATOR): Starting run")

    response = client.retrieve_docdb_records(
        filter_query={},
        limit=0,
        paginate_batch_size=100,
    )

    logging.info(f"(METADATA VALIDATOR): Retrieved {len(response)} records")

    results = []
    for record in response:
        results.append(validate_metadata(record))

    df = pd.DataFrame(results)
    # Log results
    df.to_csv("validation_results.csv", index=False)

    logging.info("(METADATA VALIDATOR) Dataframe built -- pushing to RDS")

    if len(df) < CHUNK_SIZE:
        rds_client.overwrite_table_with_df(df, RDS_TABLE_NAME)
    else:
        # chunk into CHUNK_SIZE row chunks
        logging.info("(METADATA VALIDATOR) Chunking required for RDS")
        rds_client.overwrite_table_with_df(df[0:CHUNK_SIZE], RDS_TABLE_NAME)
        for i in range(CHUNK_SIZE, len(df), CHUNK_SIZE):
            rds_client.append_df_to_table(df[i:i + CHUNK_SIZE], RDS_TABLE_NAME)

    df2 = rds_client.read_table(RDS_TABLE_NAME)
    df2.to_csv("validation_results_from_rds.csv", index=False)

    logging.info("(METADATA VALIDATOR) Success")
