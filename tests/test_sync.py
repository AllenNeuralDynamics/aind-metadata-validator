import unittest
from unittest.mock import patch
import pandas as pd
from aind_metadata_validator.sync import (
    run,
    OUTPUT_FOLDER,
    TABLE_NAME,
)


class TestSync(unittest.TestCase):

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


if __name__ == "__main__":
    unittest.main()
