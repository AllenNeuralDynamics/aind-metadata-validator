"""Test mappings."""

import unittest
from aind_metadata_validator.mappings import FIRST_LAYER_MAPPING, SECOND_LAYER_MAPPING
from aind_data_schema.core.acquisition import Acquisition
from typing import Optional, List


class CoreValidatorTest(unittest.TestCase):
    """Mappings tests."""

    def test_first_mappings(self):
        """Check that mappings are set properly"""
        self.assertEqual(FIRST_LAYER_MAPPING["acquisition"], Acquisition)

    def test_second_mappings(self):
        """Check that mappings are set properly"""
        self.assertEqual(SECOND_LAYER_MAPPING["acquisition"]["protocol_id"], List[str])
        self.assertEqual(SECOND_LAYER_MAPPING["acquisition"]["specimen_id"], str)
        self.assertEqual(SECOND_LAYER_MAPPING["acquisition"]["notes"], Optional[str])


if __name__ == "__main__":
    unittest.main()
