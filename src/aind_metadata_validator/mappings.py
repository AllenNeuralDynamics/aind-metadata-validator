# First level metadata models
from typing import Annotated, get_args, Union, get_origin

from aind_data_schema.core.metadata import Metadata
from aind_data_schema.core.acquisition import Acquisition
from aind_data_schema.core.data_description import DataDescription
from aind_data_schema.core.instrument import Instrument
from aind_data_schema.core.procedures import Procedures
from aind_data_schema.core.processing import Processing
from aind_data_schema.core.quality_control import QualityControl
from aind_data_schema.core.subject import Subject
from aind_data_schema.core.model import Model
from aind_data_schema.core.metadata import CORE_FILES

EXTRA_FIELDS = [
    "describedBy",
    "schema_version",
    "license",
    "creation_time",
    "_DESCRIBED_BY_URL",
    "_described_by_url",
]


def gen_first_layer_mapping():
    """Generate a mapping of the first layer of metadata models"""
    mapping = {}
    for field_name, field_type in Metadata.__annotations__.items():

        if field_name in CORE_FILES:

            # If the type is Union it's because it was set as Optional[Class],
            # so we grab just the class and drop the None
            if getattr(field_type, "__origin__") is Union:
                field_type = get_args(field_type)[0]

            mapping[field_name] = field_type

    return mapping


def gen_second_layer_mapping(model_class_list):
    """Generate a mapping of the second layer of metadata models

    Parameters
    ----------
    model_class : Class
        Metadata core class to generate sub-fields from
    """
    mappings = {}

    for model_class in model_class_list:
        mapping = {}
        for field_name, field_type in model_class.__annotations__.items():
            if field_name in EXTRA_FIELDS:
                continue

            mapping[field_name] = unwrap_annotated(field_type)

        mappings[model_class.default_filename().replace(".json", "")] = mapping

    return mappings


def unwrap_annotated(field_type):
    if get_origin(field_type) is Annotated:
        return get_args(field_type)[0]
    return field_type


FIRST_LAYER_MAPPING = gen_first_layer_mapping()

SECOND_LAYER_MAPPING = gen_second_layer_mapping(
    [
        Acquisition,
        DataDescription,
        Instrument,
        Procedures,
        Processing,
        QualityControl,
        Subject,
        Model,
    ]
)
