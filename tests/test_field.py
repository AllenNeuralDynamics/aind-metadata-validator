"""Field validator tests"""

from typing import Annotated, Optional, Union
import unittest
import json
from aind_data_schema.components.devices import Device
from aind_data_schema_models.data_name_patterns import DataLevel
from aind_data_schema_models.organizations import Organization
from aind_metadata_validator.utils import MetadataState
from aind_metadata_validator.field_validator import (
    validate_field_metadata,
    validate_field,
    validate_field_list,
    validate_field_optional,
    validate_field_union,
    try_instantiate,
)


class TestValidateFieldMetadata(unittest.TestCase):
    """Test field_validator"""

    def setUp(self):
        """Set up test data for validate_field_metadata tests"""
        with open("./tests/resources/data_description.json") as f:
            self.data = json.load(f)
            self.result = validate_field_metadata(
                "data_description", self.data
            )
        with open("./tests/resources/data_description_invalid.json") as f:
            self.data_invalid = json.load(f)
            self.result_invalid = validate_field_metadata(
                "data_description", self.data_invalid
            )

    def test_validate_field_metadata_platform(self):
        self.assertEqual(self.result["platform"], MetadataState.VALID)

    def test_validate_field_metadata_subject_id(self):
        self.assertEqual(self.result["subject_id"], MetadataState.VALID)

    def test_validate_field_metadata_label(self):
        self.assertEqual(self.result["label"], MetadataState.OPTIONAL)

    def test_validate_field_metadata_name(self):
        self.assertEqual(self.result["name"], MetadataState.VALID)

    def test_validate_field_metadata_institution(self):
        self.assertEqual(self.result["institution"], MetadataState.VALID)

    def test_validate_field_metadata_funding_source(self):
        self.assertEqual(self.result["funding_source"], MetadataState.VALID)

    def test_validate_field_metadata_data_level(self):
        self.assertEqual(self.result["data_level"], MetadataState.VALID)

    def test_validate_field_metadata_group(self):
        self.assertEqual(self.result["group"], MetadataState.OPTIONAL)

    def test_validate_field_metadata_investigators(self):
        self.assertEqual(self.result["investigators"], MetadataState.VALID)

    def test_validate_field_metadata_project_name(self):
        self.assertEqual(self.result["project_name"], MetadataState.VALID)

    def test_validate_field_metadata_restrictions(self):
        self.assertEqual(self.result["restrictions"], MetadataState.OPTIONAL)

    def test_validate_field_metadata_modality(self):
        self.assertEqual(self.result["modality"], MetadataState.VALID)

    def test_validate_field_metadata_related_data(self):
        self.assertEqual(self.result["related_data"], MetadataState.VALID)

    def test_validate_field_metadata_data_summary(self):
        self.assertEqual(self.result["data_summary"], MetadataState.OPTIONAL)

    def test_invalidate_field_metadata_subject(self):
        self.assertEqual(
            self.result_invalid["subject_id"], MetadataState.MISSING
        )

    def test_invalidate_field_datadesc_project_name(self):
        self.assertEqual(
            self.result_invalid["project_name"], MetadataState.OPTIONAL
        )

    def test_invalid_core_file_name(self):
        # Test that invalid core file name raises ValueError
        with self.assertRaises(ValueError):
            validate_field_metadata("invalid_core_file", self.data)

    def test_validate_field(self):
        # Example unit test for validate_field (add more cases as needed)
        self.assertEqual(
            validate_field("example_data", None, str), MetadataState.VALID
        )
        self.assertEqual(validate_field(123, None, int), MetadataState.VALID)
        self.assertEqual(
            validate_field(123.5, None, float), MetadataState.VALID
        )
        self.assertEqual(
            validate_field({"key": "value"}, None, dict), MetadataState.VALID
        )

        # Tests that pass Optional, Annotated, or Union as origin types
        self.assertEqual(
            validate_field("string", Optional, str), MetadataState.VALID
        )
        self.assertEqual(
            validate_field("string", Union, Union[str, None]),
            MetadataState.VALID,
        )
        self.assertEqual(
            validate_field(1, list, list[Annotated[Union[str, int], "none"]]),
            MetadataState.PRESENT,
        )
        self.assertEqual(
            validate_field(
                [1, 2, 3], list, list[Annotated[Union[str, int], "none"]]
            ),
            MetadataState.VALID,
        )

        # Test classes
        device = Device(
            name="device_name",
        )
        self.assertEqual(
            validate_field(device.model_dump(), None, Device),
            MetadataState.VALID,
        )
        self.assertEqual(
            validate_field(DataLevel.DERIVED.value, None, DataLevel),
            MetadataState.VALID,
        )

        # Test models
        aind = Organization.AIND
        self.assertEqual(
            validate_field(
                aind.model_dump(),
                Annotated,
                Organization.RESEARCH_INSTITUTIONS,
            ),
            MetadataState.VALID,
        )

    def test_validate_field_list(self):
        """Test the validate_field_list function"""
        self.assertEqual(
            validate_field_list([1, 2, 3], list[int]), MetadataState.VALID
        )
        self.assertEqual(
            validate_field_list(["a", "b", "c"], list[str]),
            MetadataState.VALID,
        )
        self.assertEqual(
            validate_field_list([1, 2, 3], list[Union[int, str]]),
            MetadataState.VALID,
        )
        self.assertEqual(
            validate_field_list(
                [1, 2, 3], list[Annotated[Union[int, str], "none"]]
            ),
            MetadataState.VALID,
        )

    def test_validate_field_optional(self):
        """Test the validate_field_optional function"""
        # Test validate_field_optional with empty data
        self.assertEqual(
            validate_field_optional("", str), MetadataState.OPTIONAL
        )
        self.assertEqual(
            validate_field_optional(None, str), MetadataState.OPTIONAL
        )
        self.assertEqual(
            validate_field_optional({}, str), MetadataState.OPTIONAL
        )
        self.assertEqual(
            validate_field_optional([], str), MetadataState.OPTIONAL
        )
        # Test validate_field_optional with non-empty data
        self.assertEqual(
            validate_field_optional("non_empty_data", str), MetadataState.VALID
        )
        self.assertEqual(validate_field_optional(1, int), MetadataState.VALID)
        self.assertEqual(
            validate_field_optional({"key": "value"}, dict),
            MetadataState.VALID,
        )
        self.assertEqual(
            validate_field_optional("meow", int), MetadataState.PRESENT
        )
        self.assertEqual(
            validate_field_optional(1, str), MetadataState.PRESENT
        )

    def test_validate_field_union(self):
        """Test the validate_field_union function"""
        # Test validate_field_union with valid and invalid data
        self.assertEqual(
            validate_field_union({"key": "value"}, [dict, str]),
            MetadataState.VALID,
        )
        self.assertEqual(
            validate_field_union("string_data", [dict, str]),
            MetadataState.VALID,
        )
        self.assertEqual(
            validate_field_union(123, [str, int]), MetadataState.VALID
        )
        self.assertEqual(
            validate_field_union(123, [dict, str]), MetadataState.PRESENT
        )

    def test_try_instantiate_none_type(self):
        self.assertEqual(
            try_instantiate(None, type(None)), MetadataState.OPTIONAL
        )
        self.assertEqual(
            try_instantiate("data", type(None)), MetadataState.PRESENT
        )

    def test_try_instantiate_missing_data(self):
        self.assertEqual(try_instantiate(None, str), MetadataState.MISSING)
        self.assertEqual(try_instantiate("", str), MetadataState.MISSING)

    def test_try_instantiate_general_case(self):
        self.assertEqual(try_instantiate("data", str), MetadataState.VALID)
        self.assertEqual(try_instantiate(123, int), MetadataState.VALID)

    def test_try_instantiate_dict(self):
        class DummyClass:
            def __init__(self, field):
                self.field = field

        self.assertEqual(
            try_instantiate({"field": "value"}, DummyClass),
            MetadataState.VALID,
        )
        self.assertEqual(
            try_instantiate({"wrong_field": "value"}, DummyClass),
            MetadataState.PRESENT,
        )

    def test_try_instantiate_invalid_data(self):
        self.assertEqual(try_instantiate(123, str), MetadataState.PRESENT)
        self.assertEqual(try_instantiate("data", int), MetadataState.PRESENT)


if __name__ == "__main__":
    unittest.main()
