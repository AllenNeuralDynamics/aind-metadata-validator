from enum import Enum


class FileRequirement(Enum):
    REQUIRED = 1
    OPTIONAL = 0


class MetadataState(int, Enum):
    VALID = 2  # validates as it's class
    PRESENT = 1  # present
    OPTIONAL = 0  # missing, but it's optional
    MISSING = -1  # missing, and it's required
    EXCLUDED = -2  # excluded for all modalities in the metadata
    CORRUPT = -3  # corrupt, can't be loaded from json


REMAPS = {
    "OPHYS": "POPHYS",
    "EPHYS": "ECEPHYS",
    "TRAINED_BEHAVIOR": "BEHAVIOR",
    "HSFP": "FIB",
    "DISPIM": "SPIM",
    "MULTIPLANE_OPHYS": "POPHYS",
    "SMARTSPIM": "SPIM",
    "FIP": "FIB",
    "SINGLE_PLANE_OPHYS": "POPHYS",
    "EXASPIM": "SPIM",
}
