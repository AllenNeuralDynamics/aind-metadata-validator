"""Unit tests for the sync module of aind_metadata_validator."""
import unittest
from unittest.mock import patch
import pandas as pd
from aind_metadata_validator import __version__ as version
from aind_metadata_validator.sync import (
    _fetch_unique_locations,
    _load_prev_validation_map,
    _build_results,
)


class TestSync(unittest.TestCase):
    """Unit tests for the sync module."""

    @patch("aind_metadata_validator.sync.client.aggregate_docdb_records")
    def test_fetch_unique_locations_test_mode(self, mock_agg):
        """test_mode=True should truncate the location list to 10."""
        mock_agg.return_value = [{"locations": list(range(20))}]
        result = _fetch_unique_locations(test_mode=True)
        self.assertEqual(len(result), 10)

    @patch("aind_metadata_validator.sync.custom", side_effect=Exception("DB error"))
    def test_load_prev_validation_map_exception(self, _mock):
        """Exception reading from the table should return an empty dict."""
        result = _load_prev_validation_map()
        self.assertEqual(result, {})

    @patch("aind_metadata_validator.sync.custom")
    def test_load_prev_validation_map_valid_data(self, mock_custom):
        """A sufficiently large DataFrame should be returned as a location map."""
        large_df = pd.DataFrame(
            [{"location": f"loc{i}", "validated": i} for i in range(15)]
        )
        mock_custom.return_value = large_df
        result = _load_prev_validation_map()
        self.assertEqual(len(result), 15)
        self.assertIn("loc0", result)

    @patch("aind_metadata_validator.sync.client.retrieve_docdb_records")
    def test_build_results_reuses_prev(self, mock_retrieve):
        """A matching prev record should be reused without re-validating."""
        record = {"location": "loc1", "_last_modified": "2025-01-01"}
        prev = {"location": "loc1", "_last_modified": "2025-01-01", "validator_version": version}
        mock_retrieve.return_value = [record]
        results = _build_results(["loc1"], {"loc1": prev}, force=False)
        self.assertEqual(results, [prev])




if __name__ == "__main__":
    unittest.main()
