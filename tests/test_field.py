import unittest
import json
from aind_metadata_validator.utils import MetadataState
from aind_metadata_validator.field_validator import (
    validate_field_metadata,
    validate_field,
    validate_field_optional,
    validate_field_union,
)


class TestValidateFieldMetadata(unittest.TestCase):

    def setUp(self):
        # Load the sample valid data from the JSON file
        with open('./tests/resources/data_description.json') as f:
            self.data = json.load(f)

    def test_validate_field_metadata_valid(self):
        # Test that valid data returns expected MetadataState for each field
        result = validate_field_metadata("data_description", self.data)
        self.assertEqual(result["platform"], MetadataState.PRESENT)
        self.assertEqual(result["subject_id"], MetadataState.VALID)
        self.assertEqual(result["label"], MetadataState.MISSING)
        self.assertEqual(result["name"], MetadataState.VALID)
        self.assertEqual(result["institution"], MetadataState.VALID)
        self.assertEqual(result["funding_source"], MetadataState.VALID)
        self.assertEqual(result["data_level"], MetadataState.VALID)
        self.assertEqual(result["group"], MetadataState.MISSING)
        self.assertEqual(result["investigators"], MetadataState.VALID)
        self.assertEqual(result["project_name"], MetadataState.MISSING)
        self.assertEqual(result["restrictions"], MetadataState.MISSING)
        self.assertEqual(result["modality"], MetadataState.VALID)
        self.assertEqual(result["related_data"], MetadataState.MISSING)
        self.assertEqual(result["data_summary"], MetadataState.MISSING)

    def test_invalid_core_file_name(self):
        # Test that invalid core file name raises ValueError
        with self.assertRaises(ValueError):
            validate_field_metadata("invalid_core_file", self.data)

    def test_validate_field(self):
        # Example unit test for validate_field (add more cases as needed)
        self.assertEqual(
            validate_field("example_data", None, str),
            MetadataState.VALID
        )
        self.assertEqual(
            validate_field("example_data", None, str),
            MetadataState.VALID
        )

    def test_validate_field_optional(self):
        # Test validate_field_optional with empty and non-empty data
        self.assertEqual(
            validate_field_optional("", str),
            MetadataState.VALID
        )
        self.assertEqual(
            validate_field_optional("non_empty_data", str),
            MetadataState.VALID
        )

    def test_validate_field_union(self):
        # Test validate_field_union with valid and invalid data
        self.assertEqual(
            validate_field_union({"key": "value"}, [dict, str]),
            MetadataState.VALID
        )
        self.assertEqual(
            validate_field_union("string_data", [dict, str]),
            MetadataState.VALID
        )
        self.assertEqual(
            validate_field_union(123, [dict, str]),
            MetadataState.PRESENT
        )


if __name__ == "__main__":
    unittest.main()
