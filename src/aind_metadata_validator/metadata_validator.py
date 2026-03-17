from aind_metadata_validator import __version__ as version
from aind_metadata_validator.core_validator import validate_core_metadata
from aind_metadata_validator.field_validator import validate_field_metadata
from aind_data_schema.core.metadata import Metadata
from aind_metadata_validator.mappings import CORE_FILES
from aind_data_schema.core.metadata import REQUIRED_FILE_SETS
from aind_metadata_validator.utils import (
    MetadataState,
    FileRequirement,
)
from aind_metadata_validator.mappings import SECOND_LAYER_MAPPING
import logging
from typing import Optional


def _get_file_requirements(data: dict) -> dict:
    """Determine file requirements based on modalities present in data."""
    file_requirements = {
        core_file_name: FileRequirement.OPTIONAL
        for core_file_name in CORE_FILES
    }
    for field in data.keys():
        if field in REQUIRED_FILE_SETS.keys():
            for core_file_name in REQUIRED_FILE_SETS[field]:
                file_requirements[core_file_name] = FileRequirement.REQUIRED
    return file_requirements


def _validate_core_files(
    data: dict, results: dict, file_requirements: dict
) -> None:
    """Populate results with per-core-file validation states."""
    for core_file_name in CORE_FILES:
        logging.info(
            f"(METADATA_VALIDATOR): Core file: {core_file_name} is {file_requirements[core_file_name].value}"
        )
        if core_file_name in data:
            results[core_file_name] = validate_core_metadata(
                core_file_name,
                data[core_file_name],
                file_requirements[core_file_name],
            )
        elif file_requirements[core_file_name] == FileRequirement.REQUIRED:
            results[core_file_name] = MetadataState.MISSING
        elif file_requirements[core_file_name] == FileRequirement.OPTIONAL:
            results[core_file_name] = MetadataState.OPTIONAL
        elif file_requirements[core_file_name] == FileRequirement.EXCLUDED:
            results[core_file_name] = MetadataState.EXCLUDED
        else:
            logging.error(
                f"(METADATA_VALIDATOR): Unknown file requirement for {core_file_name}"
            )


def _validate_fields(
    data: dict, results: dict, file_requirements: dict
) -> None:
    """Populate results with per-field validation states for each core file."""
    for core_file_name in CORE_FILES:
        logging.info(
            f"(METADATA_VALIDATOR): Field checks for: {core_file_name}"
        )
        if core_file_name not in data:
            continue

        expected_fields = SECOND_LAYER_MAPPING[core_file_name]
        if data[core_file_name]:
            field_results = validate_field_metadata(
                core_file_name, data[core_file_name]
            )
        else:
            requirement = file_requirements[core_file_name]
            state_map = {
                FileRequirement.REQUIRED: MetadataState.MISSING,
                FileRequirement.OPTIONAL: MetadataState.OPTIONAL,
                FileRequirement.EXCLUDED: MetadataState.EXCLUDED,
            }
            field_results = {
                field: state_map[requirement] for field in expected_fields
            }

        for field_name, field_state in field_results.items():
            results[f"{core_file_name}.{field_name}"] = field_state


def validate_metadata(
    data: dict, prev_validation: Optional[dict] = None
) -> dict:
    """Validate metadata

    Parameters
    ----------
    data : dict
        Data in dictionary format

    Returns
    -------
    dict
        Returns a dictionary with the results of the validation
    """
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    if prev_validation and "validator_version" in prev_validation:
        if (
            prev_validation["validator_version"] == version
            and prev_validation["_last_modified"] == data["_last_modified"]
        ):
            logging.info(
                f"(METADATA_VALIDATOR): Skipping validation for _id {data['_id']}"
                f"name {data['name']} as it has already been validated"
            )
            return prev_validation

    logging.info(
        f"(METADATA_VALIDATOR): Running for _id {data['_id']} name {data['name']}"
    )

    results = {"_id": data["_id"]}
    file_requirements = _get_file_requirements(data)

    logging.info("(METADATA_VALIDATOR): Full metadata")
    try:
        metadata = Metadata.model_validate(data)
        if metadata:
            results["metadata"] = MetadataState.VALID
    except Exception as e:
        logging.error(f"(METADATA_VALIDATOR): Error validating metadata: {e}")
        results["metadata"] = MetadataState.PRESENT

    _validate_core_files(data, results, file_requirements)
    _validate_fields(data, results, file_requirements)

    results["_last_modified"] = data["_last_modified"]
    results["validator_version"] = version

    return results
