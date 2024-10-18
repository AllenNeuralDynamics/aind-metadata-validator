
# First level metadata models
from typing import get_args, Union

from aind_data_schema.core.metadata import Metadata, CORE_FILES
from aind_data_schema.core.acquisition import Acquisition
from aind_data_schema.core.data_description import DataDescription
from aind_data_schema.core.instrument import Instrument
from aind_data_schema.core.procedures import Procedures
from aind_data_schema.core.processing import Processing
from aind_data_schema.core.quality_control import QualityControl
from aind_data_schema.core.rig import Rig
from aind_data_schema.core.session import Session
from aind_data_schema.core.subject import Subject

EXTRA_FIELDS = [
    'describedBy',
    'schema_version',
]


def gen_first_layer_mapping(model_class):
    """Generate a mapping of the first layer of metadata models

    Parameters
    ----------
    model_class : _type_
        _description_
    """
    mapping = {}
    for field_name, field_type in model_class.__annotations__.items():

        if field_name in CORE_FILES:
            # If the type is Union it's because it was set as Optional[Class],
            # so we grab just the class and drop the None
            if getattr(field_type, '__origin__') is Union:
                field_type = get_args(field_type)[0]
            elif isinstance(field_type, type):
                mapping[field_name] = field_type
            else:
                raise ValueError(f"Field type {field_type} is not a class or primitive type")

    return mapping


def gen_second_layer_mapping(model_class_list):
    """_summary_

    Parameters
    ----------
    model_class : _type_
        _description_
    """
    mappings = {}

    for model_class in model_class_list:
        mapping = {}
        for field_name, field_type in model_class.__annotations__.items():
            if field_name in EXTRA_FIELDS:
                continue

            mapping[field_name] = field_type

        mappings[model_class.__name__.lower()] = mapping

    return mappings


FIRST_LAYER_MAPPING = gen_first_layer_mapping(Metadata)

SECOND_LAYER_MAPPING = gen_second_layer_mapping([
    Acquisition,
    DataDescription,
    Instrument,
    Procedures,
    Processing,
    QualityControl,
    Rig,
    Session,
    Subject])