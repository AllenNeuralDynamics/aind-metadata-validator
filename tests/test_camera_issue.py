"""Test validator."""

import json
import unittest
from aind_metadata_validator.metadata_validator import validate_metadata
from aind_metadata_validator.utils import MetadataState
from aind_data_schema.core.rig import Rig
from aind_data_schema.core.metadata import Metadata


class ValidatorTest(unittest.TestCase):
    """Validator tests."""

    def setUp(self):
        """Set up the tests"""
        with open("./tests/resources/camera_issue.json") as f:
            self.data = json.load(f)
            
            print(self.data["rig"]["cameras"])

    def test_validator(self):
        """Test the main validator"""
        
        rig = self.data["rig"]
        
        # try to validate just the rig
        result = Rig.model_validate(rig)
        
        result2 = Metadata.model_validate(self.data)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result2)
        # result = validate_metadata(self.data)


if __name__ == "__main__":
    unittest.main()
