from enum import Enum
from typing import Annotated, Optional, Union, get_args, get_origin
import logging
from aind_metadata_validator.utils import MetadataState
from aind_metadata_validator.mappings import SECOND_LAYER_MAPPING, EXTRA_FIELDS


def validate_field_metadata(
    core_file_name: str, data: dict
) -> dict[str, MetadataState]:
    """Validate a metadata file's fields against their expected classes

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
        If the core file name has no expected classes in the mapping
    """
    if core_file_name not in SECOND_LAYER_MAPPING:
        raise ValueError(f"Invalid core file name: {core_file_name}")

    expected_classes = SECOND_LAYER_MAPPING[core_file_name]

    if not isinstance(data, dict):
        return {field: MetadataState.MISSING for field in expected_classes}

    out = {}
    for field_name, field_data in data.items():
        if any([ignore_field in field_name for ignore_field in EXTRA_FIELDS]):
            logging.info(f"Skipping ignored field: {field_name}")
            continue

        if field_name not in expected_classes:
            logging.warning(
                f"Field name: {field_name} is missing from the expected_classes file"
            )
            continue

        expected_class = expected_classes[field_name]
        origin_type = getattr(expected_class, "__origin__", None)

        out[field_name] = validate_field(
            field_data, origin_type, expected_class
        )

    return out


def validate_field(field_data, origin_type, expected_class) -> MetadataState:
    """Validate a metadata field against its expected class.

    Parameters
    ----------
    field_data : Any
        The data to validate.
    origin_type : Type
        The type of the field being validated.
    expected_class : Type
        The expected class/type for validation.

    Returns
    -------
    MetadataState
        Returns VALID, PRESENT, or MISSING based on the validation.

    Raises
    ------
    ValueError
        If validation fails.
    """
    # If origin_type is None, we only have to validate against the expected class
    if origin_type is None:
        return try_instantiate(field_data, expected_class)

    # Handle origin_type
    if origin_type is Annotated:
        expected_class = get_args(expected_class)[0]
        origin_type = get_origin(expected_class)
        return validate_field(field_data, origin_type, expected_class)

    if origin_type is list:
        return validate_field_list(field_data, expected_class)

    if origin_type is Optional:
        return validate_field_optional(field_data, expected_class)

    if origin_type is Union:
        union_types = get_args(expected_class)
        return validate_field_union(field_data, union_types)

    return MetadataState.PRESENT


def validate_field_list(field_data, expected_class):
    """Validate a list of data against it's expected class"""
    if not isinstance(field_data, list):
        return MetadataState.PRESENT

    item_type = get_args(expected_class)[0]
    origin_type = get_origin(item_type)

    statuses = [
        validate_field(item, origin_type, item_type) for item in field_data
    ]
    if all(status == MetadataState.VALID for status in statuses):
        return MetadataState.VALID
    else:
        return MetadataState.PRESENT


def validate_field_optional(field_data, expected_class):
    """Validate Optional[type] fields"""
    if not field_data:
        return MetadataState.OPTIONAL
    return try_instantiate(field_data, expected_class)


def validate_field_union(field_data, expected_classes):
    """Validate Union[type, type] fields"""
    states = [try_instantiate(field_data, cls) for cls in expected_classes]
    if MetadataState.VALID in states:
        return MetadataState.VALID
    if MetadataState.PRESENT in states:
        return MetadataState.PRESENT
    if MetadataState.OPTIONAL in states:
        return MetadataState.OPTIONAL
    return MetadataState.MISSING


def try_instantiate(field_data, expected_class):
    """Get the metadata state based on instantiating as a specific class"""
    if expected_class is type(None):
        # This condition handles Optional[], where it's okay for data to be missing
        return MetadataState.PRESENT if field_data else MetadataState.OPTIONAL
    elif not field_data:
        # Missing data that is not Optional
        return MetadataState.MISSING

    # Special cases
    try:
        if isinstance(field_data, dict):
            expected_class(**field_data)
            return MetadataState.VALID
        elif isinstance(field_data, expected_class):
            return MetadataState.VALID
        elif issubclass(expected_class, Enum):
            expected_class(field_data)
        else:
            return MetadataState.PRESENT
        
        # If we get here... what state are we even in?
        return MetadataState.VALID
    except Exception:
        return MetadataState.PRESENT
