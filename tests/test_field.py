import unittest
from aind_metadata_validator.utils import MetadataState
from aind_metadata_validator.field_validator import validate_field_metadata, validate_field, IGNORED_FIELDS
import json


class TestFieldValidator(unittest.TestCase):

    def setUp(self):
        with open('./tests/resources/data_description.json') as f:
            self.data = json.load(f)

    def test_validate_field_metadata_valid(self):
        # Test that valid data returns VALID for each field
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

    def test_validate_field_metadata_invalid_field(self):
        # Add an unexpected field to test PRESENT state
        self.data["unknown_field"] = "unexpected_value"
        result = validate_field_metadata("data_description", self.data)
        self.assertTrue("unknown_field" not in result)

    def test_validate_field_metadata_missing_field(self):
        # Remove an essential field and expect it to be marked as MISSING
        self.data["subject_id"] = None
        result = validate_field_metadata("data_description", self.data)
        self.assertEqual(result["subject_id"], MetadataState.MISSING)

    def test_validate_field_metadata_invalid_core_file(self):
        # Test with an invalid core file name
        with self.assertRaises(ValueError):
            validate_field_metadata("invalid_file_name", self.data)

    def test_validate_field_valid(self):
        # Validate a single valid field and expect VALID
        field_data = {"name": "Electrophysiology platform", "abbreviation": "ecephys"}
        self.assertEqual(validate_field(field_data, dict), MetadataState.VALID)

    def test_validate_field_missing(self):
        # Validate an empty field and expect MISSING
        field_data = None
        self.assertEqual(validate_field(field_data, dict), MetadataState.MISSING)

    def test_validate_field_present_invalid_data(self):
        # Validate an incorrect field format to expect PRESENT
        field_data = "invalid_data_format"
        self.assertEqual(validate_field(field_data, dict), MetadataState.PRESENT)


if __name__ == '__main__':
    unittest.main()
