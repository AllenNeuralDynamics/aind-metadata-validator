# aind-metadata-validator

This package includes helper functions for validating metadata from `aind-data-schema`, individual files in a metadata.json file, and the fields within each file.

All validation returns a `MetadataState` enum, see `utils.py`

## Get status

### By ID

Use aind-data-access-api [todo]

### Full table

You can get the entire redshift status table by running:

```
from aind_data_access_api.rds_tables import RDSCredentials
from aind_data_access_api.rds_tables import Client
import pandas as pd

DEV_OR_PROD = "dev" if "test" in API_GATEWAY_HOST else "prod"
REDSHIFT_SECRETS = f"/aind/{DEV_OR_PROD}/redshift/credentials/readwrite"
RDS_TABLE_NAME = f"metadata_status_{DEV_OR_PROD}"

rds_client = Client(
        credentials=RDSCredentials(
            aws_secrets_name=REDSHIFT_SECRETS
        ),
    )

class MetadataState(int, Enum):
    VALID = 2  # validates as it's class
    PRESENT = 1  # present
    OPTIONAL = 0  # missing, but it's optional
    MISSING = -1  # missing, and it's required
    EXCLUDED = -2  # excluded for all modalities in the metadata
    CORRUPT = -3  # corrupt, can't be loaded from json


def _get_status() -> pd.DataFrame:
    """Get the status of the metadata
    """
    response = rds_client.read_table(RDS_TABLE_NAME)

    # returns int values, can be compared against MetadataState
    return response
```

## Metadata validation

Returns a dictionary where each key is `metadata`, a `file`, or a `file.field` and the value is the `MetadataState`.

```
from aind_metadata_validator.metadata_validator import validate_metadata

m = Metadata()

results_df = validate_metadata(m.model_dump())
```

## Redshift sync

### Run on Code Ocean

Two code ocean capsules run the sync nightly: https://codeocean.allenneuraldynamics.org/capsule/0257223/tree and https://codeocean.allenneuraldynamics-test.org/capsule/3640490/tree

### Run locally

The package also includes a function `run()` in `sync.py` that will validate the entire DocDB and push the results to redshift.

`pip install aind-metadata-validator`

```
from aind_metadata_validator.sync import run

run()
```
