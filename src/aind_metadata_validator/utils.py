from enum import Enum


class MetadataState(str, Enum):
    VALID = "valid"  # validates as it's class
    PRESENT = "present"  # present
    OPTIONAL = "optional"  # missing, but it's optional
    MISSING = "missing"  # missing, and it's required
    EXCLUDED = "excluded"  # excluded for all modalities in the metadata
    CORRUPT = "corrupt"  # present, but the corresponding JSON data is corrupt in S3
