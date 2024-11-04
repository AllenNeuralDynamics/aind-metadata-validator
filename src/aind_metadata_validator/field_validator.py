from typing import Annotated, Optional, Union, get_args

from pydantic import ValidationError
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
        origin_type = get_type(origin_type)

        if origin_type is Optional and not field_data:
            out[field_name] = MetadataState.VALID
            continue

        # Check for missing data
        if not field_data or field_data == "" or field_data == {} or field_data == []:
            out[field_name] = MetadataState.MISSING
            continue

        if origin_type is list:
            item_type = expected_class.__args__[0]
            item_type = get_type(item_type)

            print(item_type)

            if all([item_type(**item) for item in field_data]):
                out[field_name] = MetadataState.VALID
            else:
                out[field_name] = MetadataState.PRESENT

        elif origin_type is Union:
            union_types = get_args(expected_class)

            for union_type in union_types:
                try:
                    if isinstance(field_data, dict):
                        union_type(**field_data)
                    else:
                        union_type(field_data)
                    out[field_name] = MetadataState.VALID
                    break
                except ValidationError:
                    continue
            out[field_name] = MetadataState.PRESENT

        else:
            out[field_name] = validate_field(field_data, expected_class)

    return out


def get_type(type):
    """Parse Annotated/Union/Optional types and get the real type back"""
    if type is Annotated:
        return get_args(type)[0]
    elif type is Union:
        return get_args(type)[0]
    elif type is Optional:
        return get_args(type)[0]
    else:
        return type


def validate_field(field_data: dict, expected_class) -> MetadataState:
    """Validate a metadata field against its expected class

    Parameters
    ----------
    field_data : dict
        Data in dictionary format
    expected_class : Class
        Expected class

    Returns
    -------
    MetadataState
        Returns VALID or PRESENT

    Raises
    ------
    ValueError
        _description_
    """

    try:
        expected_class(**field_data)
        return MetadataState.VALID
    except Exception:
        if field_data:
            return MetadataState.PRESENT
        else:
            return MetadataState.MISSING
