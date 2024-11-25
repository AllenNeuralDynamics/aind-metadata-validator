"""Test core validators."""

import unittest
from aind_metadata_validator.core_validator import validate_core_metadata
from aind_metadata_validator.utils import MetadataState
from aind_data_schema_models.modalities import FileRequirement
import json


class CoreValidatorTest(unittest.TestCase):
    """Core validator tests."""

    def test_core_validator(self):
        """Check that the core validator works"""

        with open("./tests/resources/data_description.json") as f:
            data_dict = json.load(f)

        self.assertIsNotNone(
            validate_core_metadata(
                "data_description", data_dict, FileRequirement.REQUIRED
            )
        )
        self.assertIsNotNone(
            validate_core_metadata(
                "data_description", data_dict, FileRequirement.EXCLUDED
            )
        )
        self.assertIsNotNone(
            validate_core_metadata(
                "data_description", data_dict, FileRequirement.OPTIONAL
            )
        )

        # check that Present is returned if the core file fails to validate
        data_dict["subject_id"] = None

        self.assertEqual(
            validate_core_metadata(
                "data_description", data_dict, FileRequirement.REQUIRED
            ),
            MetadataState.PRESENT,
        )

    def test_core_validator_name(self):
        """Value error should be raised for invalid filenames"""

        self.assertRaises(
            ValueError,
            validate_core_metadata,
            "invalid_file_name",
            {},
            FileRequirement.REQUIRED,
        )


if __name__ == "__main__":
    unittest.main()
