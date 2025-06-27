"""Test validator."""

import json
import unittest
from aind_metadata_validator.metadata_validator import validate_metadata


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
            "_id": "f5d7c192-e13a-4273-a601-f4adaf76b88d",
            "metadata": 2,
            "subject": 2,
            "data_description": 2,
            "procedures": 2,
            "instrument": 2,
            "processing": 2,
            "acquisition": 2,
            "quality_control": 2,
            "model": 0,
            "subject.object_type": 1,
            "subject.subject_id": 2,
            "subject.subject_details": 1,
            "subject.notes": 0,
            "data_description.object_type": 1,
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
            "data_description.data_summary": 2,
            "procedures.object_type": 1,
            "procedures.subject_id": 2,
            "procedures.subject_procedures": 1,
            "procedures.specimen_procedures": 2,
            "procedures.coordinate_system": 2,
            "procedures.notes": 0,
            "instrument.object_type": 1,
            "instrument.location": 0,
            "instrument.instrument_id": 2,
            "instrument.modification_date": 1,
            "instrument.modalities": 2,
            "instrument.calibrations": 0,
            "instrument.coordinate_system": 2,
            "instrument.temperature_control": 0,
            "instrument.notes": 0,
            "instrument.connections": 2,
            "instrument.components": 1,
            "processing.object_type": 1,
            "processing.data_processes": 2,
            "processing.pipelines": 0,
            "processing.notes": 0,
            "processing.dependency_graph": 1,
            "acquisition.object_type": 1,
            "acquisition.subject_id": 2,
            "acquisition.specimen_id": 0,
            "acquisition.acquisition_start_time": 1,
            "acquisition.acquisition_end_time": 1,
            "acquisition.experimenters": 2,
            "acquisition.protocol_id": 0,
            "acquisition.ethics_review_id": 0,
            "acquisition.instrument_id": 2,
            "acquisition.acquisition_type": 2,
            "acquisition.notes": 0,
            "acquisition.coordinate_system": 0,
            "acquisition.calibrations": 2,
            "acquisition.maintenance": 2,
            "acquisition.data_streams": 2,
            "acquisition.stimulus_epochs": 2,
            "acquisition.subject_details": 2,
            "quality_control.object_type": 1,
            "quality_control.metrics": 1,
            "quality_control.key_experimenters": 0,
            "quality_control.notes": 0,
            "quality_control.default_grouping": 2,
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
            "model.object_type": 0,
        }

        for field in results:
            if field not in ["_last_modified", "validator_version"]:
                self.assertEqual(results[field], expected[field])


if __name__ == "__main__":
    unittest.main()
