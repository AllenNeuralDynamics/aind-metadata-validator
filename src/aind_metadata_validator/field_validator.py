from typing import Annotated, Optional, Union, get_args

from aind_metadata_validator.utils import MetadataState
from aind_metadata_validator.mappings import SECOND_LAYER_MAPPING


IGNORED_FIELDS = ["describedBy", "schema_version", "license", "creation_time"]


def validate_field_metadata(core_file_name: str, data: dict) -> dict[str, MetadataState]:
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

    out = {}
    for field_name, field_data in data.items():
        if field_name in IGNORED_FIELDS:
            continue

        if field_name not in expected_classes:
            print(f"Warning: field name: {field_name} is missing from the expected_classes file")
            continue

        # Data is present, try to coerce it to the expected class
        expected_class = expected_classes[field_name]

        # Handle list/optional/union/annotated
        origin_type = getattr(expected_class, "__origin__", None)

        out[field_name] = validate_field(field_data, origin_type, expected_class)

    return out


def validate_field(field_data, origin_type, expected_class) -> MetadataState:
    """Validate a metadata field against its expected class

    Parameters
    ----------
    field_data : Any
    expected_class : Class/type

    Returns
    -------
    MetadataState
        Returns VALID or PRESENT

    Raises
    ------
    ValueError
        _description_
    """

    print((field_data, origin_type, expected_class))

    # Handle optional fields that are empty
    if origin_type is Optional:
        validate_field_optional(field_data, expected_class)

    # Annotated fields get unwrapped
    if origin_type is Annotated:
        expected_class = get_args(expected_class)[0]

    # If we're here the field is not optional
    if not field_data or field_data == "" or field_data == {} or field_data == []:
        return MetadataState.MISSING

    # Deal with lists
    if origin_type is list:

        # Handle list[Annotated[Union[...]]]
        if getattr(expected_class.__args__[0], "__origin__", None) is Union:
            union_types = get_args(expected_class.__args__[0])
            return validate_field_union(field_data, union_types)

    # Deal with unions
    elif origin_type is Union:
        union_types = get_args(expected_class)
        return validate_field_union(field_data, union_types)

    # If we're here, just validate directly
    return try_instantiate(field_data, expected_class)


def validate_field_optional(field_data, expected_class):
    if field_data:
        return validate_field(field_data, expected_class, expected_class)
    return MetadataState.VALID


def validate_field_union(field_data, expected_classes):
    states = [try_instantiate(field_data, expected_class) for expected_class in expected_classes]

    if MetadataState.VALID in states:
        return MetadataState.VALID
    return MetadataState.PRESENT


def try_instantiate(field_data, expected_class):
    try:
        if isinstance(field_data, dict):
            expected_class(**field_data)
        else:
            expected_class(field_data)
        return MetadataState.VALID
    except Exception:
        return MetadataState.PRESENT