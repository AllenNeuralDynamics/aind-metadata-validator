from aind_metadata_validator.core_validator import validate_core_metadata
from aind_metadata_validator.field_validator import validate_field_metadata
from aind_data_schema.core.metadata import Metadata
from aind_metadata_validator.mappings import CORE_FILES
from aind_metadata_validator.utils import (
    MetadataState,
    FileRequirement,
)
from aind_metadata_validator.mappings import SECOND_LAYER_MAPPING
import logging


def validate_metadata(data: dict) -> dict:
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
    logging.info(
        f"(METADATA_VALIDATOR): Running for _id {data['_id']} name {data['name']}"
    )

    results = {"_id": data["_id"]}

    # The first thing we'll do is try to get the expected_files for the modalities
    file_requirements = {
        "subject": FileRequirement.REQUIRED,
        "data_description": FileRequirement.REQUIRED,
        "procedures": FileRequirement.REQUIRED,
        "instrument": FileRequirement.REQUIRED,
        "acquisition": FileRequirement.REQUIRED,
    }
    for core_file_name in CORE_FILES:
        if core_file_name not in file_requirements:
            file_requirements[core_file_name] = FileRequirement.OPTIONAL

    # Try to validate everything
    logging.info("(METADATA_VALIDATOR): Full metadata")
    try:
        metadata = Metadata.model_validate(data)
        if metadata:
            results["metadata"] = MetadataState.VALID
    except Exception as e:
        logging.error(f"(METADATA_VALIDATOR): Error validating metadata: {e}")
        results["metadata"] = MetadataState.PRESENT

    # Loop through core files
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

    # Loop through to check fields
    for core_file_name in CORE_FILES:
        logging.info(
            f"(METADATA_VALIDATOR): Field checks for: {core_file_name}"
        )

        if core_file_name in data:

            # Get the expected fields for this core file
            expected_fields = SECOND_LAYER_MAPPING[core_file_name]

            if data[core_file_name]:
                field_results = validate_field_metadata(
                    core_file_name, data[core_file_name]
                )
            else:
                if (
                    file_requirements[core_file_name]
                    == FileRequirement.REQUIRED
                ):
                    field_results = {
                        field: MetadataState.MISSING
                        for field in expected_fields
                    }
                elif (
                    file_requirements[core_file_name]
                    == FileRequirement.OPTIONAL
                ):
                    field_results = {
                        field: MetadataState.OPTIONAL
                        for field in expected_fields
                    }
                elif (
                    file_requirements[core_file_name]
                    == FileRequirement.EXCLUDED
                ):
                    field_results = {
                        field: MetadataState.EXCLUDED
                        for field in expected_fields
                    }

            for field_name, field_state in field_results.items():
                results[f"{core_file_name}.{field_name}"] = field_state

    return results
