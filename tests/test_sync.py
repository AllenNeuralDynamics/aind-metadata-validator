"""Unit tests for the sync module of aind_metadata_validator."""
import unittest
from unittest.mock import patch
import pandas as pd
from aind_metadata_validator import __version__ as version
from aind_metadata_validator.sync import (
    run,
    OUTPUT_FOLDER,
    TABLE_NAME,
    _fetch_unique_locations,
    _load_prev_validation_map,
    _build_results,
)


class TestSync(unittest.TestCase):
    """Unit tests for the sync module."""

    @patch("aind_metadata_validator.sync.client.aggregate_docdb_records")
    @patch("aind_metadata_validator.sync.client.retrieve_docdb_records")
    @patch("aind_metadata_validator.sync.validate_metadata")
    @patch("aind_metadata_validator.sync.custom")
    @patch("pandas.DataFrame.to_csv")
    def test_run(
        self,
        mock_to_csv,
        mock_custom,
        mock_validate_metadata,
        mock_retrieve_docdb_records,
        mock_aggregate_docdb_records,
    ):
        """Test the run function with mocked dependencies."""
        existing_df = pd.DataFrame(
            [
                {"validated": 1, "location": "loc1"},
                {"validated": 2, "location": "loc2"},
            ]
        )
        # custom(name) returns the df; custom(name, df) is a write and returns None
        mock_custom.side_effect = lambda name, df=None: (
            existing_df if df is None else None
        )

        # Mock the responses
        mock_aggregate_docdb_records.return_value = [
            {"locations": ["loc1", "loc2"]}
        ]
        mock_retrieve_docdb_records.return_value = [
            {"record": 1, "location": "loc1"},
            {"record": 2, "location": "loc2"},
        ]
        mock_validate_metadata.side_effect = lambda x, y: {
            "validated": x["record"]
        }

        # Run the function
        run()

        # Check if aggregate_docdb_records was called
        mock_aggregate_docdb_records.assert_called_once()

        # Check if retrieve_docdb_records was called
        mock_retrieve_docdb_records.assert_called_once_with(
            filter_query={"location": {"$in": ["loc1", "loc2"]}},
            limit=0,
            paginate_batch_size=100,
        )

        # Check if validate_metadata was called for each record
        self.assertEqual(mock_validate_metadata.call_count, 2)

        # Check if DataFrame.to_csv was called
        mock_to_csv.assert_called_once_with(
            OUTPUT_FOLDER / "validation_results.csv", index=False
        )

        # Check that custom was called to write the table and then to verify it
        self.assertEqual(mock_custom.call_count, 3)
        mock_custom.assert_any_call(TABLE_NAME)
        mock_custom.assert_any_call(TABLE_NAME, unittest.mock.ANY)

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

    @patch("aind_metadata_validator.sync.client.aggregate_docdb_records")
    @patch("aind_metadata_validator.sync.client.retrieve_docdb_records")
    @patch("aind_metadata_validator.sync.validate_metadata")
    @patch("aind_metadata_validator.sync.custom")
    @patch("pandas.DataFrame.to_csv")
    def test_run_test_mode(
        self,
        mock_to_csv,
        mock_custom,
        mock_validate_metadata,
        mock_retrieve_docdb_records,
        mock_aggregate_docdb_records,
    ):
        """run(test_mode=True) should skip the table write and only log."""
        small_df = pd.DataFrame([{"location": "loc1"}])
        mock_custom.return_value = small_df  # always returns same df
        mock_aggregate_docdb_records.return_value = [{"locations": ["loc1"]}]
        mock_retrieve_docdb_records.return_value = [{"record": 1, "location": "loc1"}]
        mock_validate_metadata.side_effect = lambda x, y: {"validated": x["record"]}

        run(test_mode=True)

        # custom should be called for _load_prev_validation_map and roundtrip only (not write)
        write_calls = [c for c in mock_custom.call_args_list if c.args and len(c.args) > 1]
        self.assertEqual(len(write_calls), 0)

    @patch("aind_metadata_validator.sync.client.aggregate_docdb_records")
    @patch("aind_metadata_validator.sync.client.retrieve_docdb_records")
    @patch("aind_metadata_validator.sync.validate_metadata")
    @patch("aind_metadata_validator.sync.custom")
    @patch("pandas.DataFrame.to_csv")
    def test_run_length_mismatch(
        self,
        mock_to_csv,
        mock_custom,
        mock_validate_metadata,
        mock_retrieve_docdb_records,
        mock_aggregate_docdb_records,
    ):
        """run() should log an error when the roundtrip row count doesn't match."""
        small_df = pd.DataFrame([{"location": "loc1"}])  # 1 row, < 10 → prev_map={}
        empty_df = pd.DataFrame()  # roundtrip returns 0 rows

        # Call order: 1) _load_prev_validation_map read, 2) write, 3) roundtrip read
        mock_custom.side_effect = [small_df, None, empty_df]
        mock_aggregate_docdb_records.return_value = [{"locations": ["loc1"]}]
        mock_retrieve_docdb_records.return_value = [{"record": 1, "location": "loc1"}]
        mock_validate_metadata.side_effect = lambda x, y: {"validated": x["record"]}

        run()  # should not raise; logs an error internally


if __name__ == "__main__":
    unittest.main()
