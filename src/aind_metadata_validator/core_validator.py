from aind_metadata_validator.utils import MetadataState
from aind_metadata_validator.mappings import FIRST_LAYER_MAPPING


def validate_core_metadata(core_file_name: str, data: dict) -> MetadataState:
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
    expected_class = FIRST_LAYER_MAPPING.get(core_file_name, None)

    if not expected_class:
        raise ValueError(f"Invalid core file name: {core_file_name}")

    try:
        expected_class(**data)
        return MetadataState.VALID
    except Exception:
        return MetadataState.PRESENT
