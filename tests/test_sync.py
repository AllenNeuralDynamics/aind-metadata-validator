import unittest
from unittest.mock import patch
import pandas as pd
from aind_metadata_validator.sync import (
    run,
    OUTPUT_FOLDER,
    CHUNK_SIZE,
    RDS_TABLE_NAME,
)


class TestSync(unittest.TestCase):

    @patch("aind_metadata_validator.sync.client.aggregate_docdb_records")
    @patch("aind_metadata_validator.sync.client.retrieve_docdb_records")
    @patch("aind_metadata_validator.sync.validate_metadata")
    @patch("aind_metadata_validator.sync.rds_client.overwrite_table_with_df")
    @patch("aind_metadata_validator.sync.rds_client.append_df_to_table")
    @patch("aind_metadata_validator.sync.rds_client.read_table")
    @patch("pandas.DataFrame.to_csv")
    def test_run(
        self,
        mock_to_csv,
        mock_read_table,
        mock_append_df_to_table,
        mock_overwrite_table_with_df,
        mock_validate_metadata,
        mock_retrieve_docdb_records,
        mock_aggregate_docdb_records,
    ):
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
        mock_read_table.return_value = pd.DataFrame(
            [
                {"validated": 1, "location": "loc1"},
                {"validated": 2, "location": "loc2"},
            ]
        )

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

        # Check if overwrite_table_with_df was called
        mock_overwrite_table_with_df.assert_called_once()

        # Check if append_df_to_table was not called (since CHUNK_SIZE > len(df))
        mock_append_df_to_table.assert_not_called()

        # Check if read_table was called twice (once for initial read, once for verification)
        self.assertEqual(mock_read_table.call_count, 2)
        mock_read_table.assert_any_call(RDS_TABLE_NAME)

    @patch("aind_metadata_validator.sync.client.aggregate_docdb_records")
    @patch("aind_metadata_validator.sync.client.retrieve_docdb_records")
    @patch("aind_metadata_validator.sync.validate_metadata")
    @patch("aind_metadata_validator.sync.rds_client.overwrite_table_with_df")
    @patch("aind_metadata_validator.sync.rds_client.append_df_to_table")
    @patch("aind_metadata_validator.sync.rds_client.read_table")
    @patch("pandas.DataFrame.to_csv")
    def test_run_with_chunking(
        self,
        mock_to_csv,
        mock_read_table,
        mock_append_df_to_table,
        mock_overwrite_table_with_df,
        mock_validate_metadata,
        mock_retrieve_docdb_records,
        mock_aggregate_docdb_records,
    ):
        # Mock the responses
        locations = [f"loc{i}" for i in range(CHUNK_SIZE + 1)]
        mock_aggregate_docdb_records.return_value = [{"locations": locations}]
        
        # Create a side effect function that returns records matching the filter
        def mock_retrieve_side_effect(filter_query, limit=0, paginate_batch_size=100):
            chunk_locations = filter_query["location"]["$in"]
            return [
                {"record": int(loc.replace("loc", "")), "location": loc}
                for loc in chunk_locations
                if loc in locations
            ]
        
        mock_retrieve_docdb_records.side_effect = mock_retrieve_side_effect
        mock_validate_metadata.side_effect = lambda x, y: {
            "validated": x["record"]
        }
        mock_read_table.return_value = pd.DataFrame(
            [
                {"validated": i, "location": f"loc{i}"}
                for i in range(CHUNK_SIZE + 1)
            ]
        )

        # Run the function
        run()

        # Check if aggregate_docdb_records was called
        mock_aggregate_docdb_records.assert_called_once()

        # Check if retrieve_docdb_records was called multiple times (11 times for 1001 locations in chunks of 100)
        expected_calls = 11  # 1001 locations / 100 per chunk = 11 chunks
        self.assertEqual(mock_retrieve_docdb_records.call_count, expected_calls)

        # Check if validate_metadata was called for each record
        self.assertEqual(mock_validate_metadata.call_count, CHUNK_SIZE + 1)

        # Check if DataFrame.to_csv was called
        mock_to_csv.assert_called_once_with(
            OUTPUT_FOLDER / "validation_results.csv", index=False
        )

        # Check if overwrite_table_with_df was called
        mock_overwrite_table_with_df.assert_called_once()

        # Check if append_df_to_table was called
        self.assertEqual(mock_append_df_to_table.call_count, 1)

        # Check if read_table was called twice (once for initial read, once for verification)
        self.assertEqual(mock_read_table.call_count, 2)
        mock_read_table.assert_any_call(RDS_TABLE_NAME)


if __name__ == "__main__":
    unittest.main()
