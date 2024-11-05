from aind_metadata_validator.utils import MetadataState
from aind_metadata_validator.mappings import FIRST_LAYER_MAPPING
from aind_metadata_validator.utils import FileRequirement
import logging


def validate_core_metadata(
    core_file_name: str, data: dict, requirement
) -> MetadataState:
    """Validate a core metadata file's data against the expected class

    Parameters
    ----------
    core_file_name : str
        File name
    data : dict
        Data in dictionary format

    Returns
    -------
    MetadataState
        Returns VALID or INVALID

    Raises
    ------
    ValueError
        _description_
    """
    if core_file_name not in FIRST_LAYER_MAPPING:
        raise ValueError(f"Invalid core file name: {core_file_name}")

    expected_class = FIRST_LAYER_MAPPING[core_file_name]

    # Check for missing data
    if not data or data == "" or data == {} or data == []:
        if requirement == FileRequirement.REQUIRED:
            return MetadataState.MISSING
        elif requirement == FileRequirement.OPTIONAL:
            return MetadataState.OPTIONAL
        elif requirement == FileRequirement.EXCLUDED:
            return MetadataState.EXCLUDED
        else:
            raise ValueError(f"Invalid requirement: {requirement}")

    # If we have data, check if we should have been excluded
    if requirement == FileRequirement.EXCLUDED:
        return MetadataState.EXCLUDED

    try:
        expected_class(**data)
        return MetadataState.VALID
    except Exception as e:
        logging.error(
            f"(METADATA_VALIDATOR): Error validating core file {core_file_name}: {e}"
        )
        return MetadataState.PRESENT
