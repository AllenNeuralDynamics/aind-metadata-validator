"""Test validator."""

import json
import unittest
from unittest.mock import patch
from aind_data_schema.core.metadata import CORE_FILES
from aind_metadata_validator import __version__ as version
from aind_metadata_validator.metadata_validator import (
    validate_metadata,
    _validate_core_files,
)
from aind_metadata_validator.utils import FileRequirement, MetadataState


class ValidatorTest(unittest.TestCase):
    """Validator tests."""

    def setUp(self):
        """Set up the tests"""
        with open("./tests/resources/metadata.json") as f:
            self.data = json.load(f)

    def test_validator(self):
        """Test the main validator"""
        results = validate_metadata(self.data)
        expected = {
            "_id": "c1496d04-844d-4855-98a4-66aeae5887f9",
            "metadata": 2,
            "subject": 2,
            "data_description": 2,
            "procedures": 2,
            "instrument": 2,
            "processing": 2,
            "acquisition": 2,
            "quality_control": 2,
            "model": 0,
            "subject.subject_id": 2,
            "subject.subject_details": 1,
            "subject.notes": 0,
            "data_description.license": 2,
            "data_description.subject_id": 2,
            "data_description.tags": 0,
            "data_description.name": 2,
            "data_description.institution": 2,
            "data_description.funding_source": 2,
            "data_description.data_level": 2,
            "data_description.group": 0,
            "data_description.investigators": 2,
            "data_description.project_name": 2,
            "data_description.restrictions": 0,
            "data_description.modalities": 2,
            "data_description.source_data": 1,
            "data_description.data_summary": 2,
            "procedures.subject_id": 2,
            "procedures.subject_procedures": 2,
            "procedures.specimen_procedures": 2,
            "procedures.coordinate_system": 2,
            "procedures.notes": 0,
            "instrument.location": 0,
            "instrument.instrument_id": 2,
            "instrument.modification_date": 1,
            "instrument.modalities": 2,
            "instrument.calibrations": 0,
            "instrument.coordinate_system": 2,
            "instrument.temperature_control": 0,
            "instrument.notes": 0,
            "instrument.connections": 2,
            "instrument.components": 2,
            "processing.data_processes": 2,
            "processing.pipelines": 0,
            "processing.notes": 0,
            "processing.dependency_graph": 0,
            "acquisition.subject_id": 2,
            "acquisition.specimen_id": 0,
            "acquisition.acquisition_start_time": 1,
            "acquisition.acquisition_end_time": 1,
            "acquisition.experimenters": 2,
            "acquisition.protocol_id": 0,
            "acquisition.ethics_review_id": 1,
            "acquisition.instrument_id": 2,
            "acquisition.acquisition_type": 2,
            "acquisition.notes": 2,
            "acquisition.coordinate_system": 0,
            "acquisition.calibrations": 2,
            "acquisition.maintenance": 2,
            "acquisition.data_streams": 2,
            "acquisition.stimulus_epochs": 2,
            "acquisition.manipulations": 2,
            "acquisition.subject_details": 2,
            "quality_control.metrics": 2,
            "quality_control.key_experimenters": 0,
            "quality_control.notes": 0,
            "quality_control.default_grouping": 1,
            "quality_control.allow_tag_failures": 2,
            "quality_control.status": 2,
            "model.name": 0,
            "model.version": 0,
            "model.example_run_code": 0,
            "model.architecture": 0,
            "model.software_framework": 0,
            "model.architecture_parameters": 0,
            "model.intended_use": 0,
            "model.limitations": 0,
            "model.training": 0,
            "model.evaluations": 0,
            "model.notes": 0,
            "_last_modified": "2025-12-02T05:51:55.235Z",
            "validator_version": "0.11.5",
        }

        for field in results:
            if field not in ["_last_modified", "validator_version"]:
                self.assertEqual(results[field], expected[field])

    def test_prev_validation_returns_early(self):
        """Test that validate_metadata returns early when prev_validation matches."""
        prev = {
            "validator_version": version,
            "_last_modified": self.data["_last_modified"],
            "_id": self.data["_id"],
        }
        result = validate_metadata(
            {
                "_last_modified": self.data["_last_modified"],
                "_id": self.data["_id"],
                "name": self.data["name"],
            },
            prev_validation=prev,
        )
        self.assertEqual(result, prev)

    def test_metadata_validate_exception(self):
        """Test that a Metadata.model_validate exception results in PRESENT state."""
        with patch(
            "aind_metadata_validator.metadata_validator.Metadata.model_validate",
            side_effect=Exception("Parse error"),
        ):
            result = validate_metadata(self.data)
            self.assertEqual(result["metadata"], MetadataState.PRESENT)

    def test_missing_core_files(self):
        """Test validation with required and optional core files absent from data."""
        # 'subject' key in data makes data_description/procedures/instrument/acquisition REQUIRED.
        # All other core files are OPTIONAL and also absent → covers lines 44-47 and 63.
        minimal_data = {
            "_id": "test-missing-id",
            "_last_modified": "2025-01-01T00:00:00.000Z",
            "name": "test",
            "subject": {"subject_id": "123"},
        }
        result = validate_metadata(minimal_data)
        self.assertEqual(result["data_description"], MetadataState.MISSING)
        self.assertEqual(result["model"], MetadataState.OPTIONAL)

    def test_unknown_file_requirement_logs_error(self):
        """Test that _validate_core_files handles an unknown file requirement."""

        class _FakeRequirement:
            value = "unknown"

        results = {}
        fake_requirements = {core: FileRequirement.OPTIONAL for core in CORE_FILES}
        first_core = CORE_FILES[0]
        fake_requirements[first_core] = _FakeRequirement()
        # Empty data → no core file is "in data", hitting elif/else branches
        _validate_core_files({}, results, fake_requirements)
        # The else branch logs an error but does not set a result
        self.assertNotIn(first_core, results)


if __name__ == "__main__":
    unittest.main()
