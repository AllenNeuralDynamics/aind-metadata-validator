# aind-metadata-validator

This package includes helper functions for validating metadata from `aind-data-schema`, individual files in a metadata.json file, and the fields within each file.

All validation returns a `MetadataState` enum, see `utils.py`

## Metadata validation

Returns a dictionary where each key is `metadata`, a `file`, or a `file.field` and the value is the `MetadataState`.

```
from aind_metadata_validator.metadata_validator import validate_metadata

m = Metadata()

results_df = validate_metadata(m.model_dump())
```

## Redshift sync

The package also includes a function `run()` in `sync.py` that will validate the entire DocDB and push the results to redshift.

`pip install aind-metadata-validator`

```
from aind_metadata_validator.sync import run

run()
```
