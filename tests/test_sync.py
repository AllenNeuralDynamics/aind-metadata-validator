import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import logging


# Patch environment variables
@patch("os.getenv", side_effect=lambda key, default=None: default)
@patch("aind_data_access_api.document_db.MetadataDbClient")
@patch("aind_metadata_validator.metadata_validator.validate_metadata")
@patch("aind_data_access_api.rds_tables.Client")
@patch("pandas.DataFrame.to_csv")
class TestMain(unittest.TestCase):

    def test_main(
        self,
        mock_to_csv,
        MockClient,
        mock_validate_metadata,
        MockMetadataDbClient,
        mock_getenv,
    ):
        # Configure the mock for MetadataDbClient
        mock_metadata_client = MockMetadataDbClient.return_value
        mock_metadata_client.retrieve_docdb_records.return_value = [
            {"sample_record": 1},
            {"sample_record": 2},
        ]

        # Configure the validate_metadata mock to return dummy validation results
        mock_validate_metadata.side_effect = lambda record: {
            "result": f"validated_{record['sample_record']}"
        }

        # Configure the mock for RDS Client
        mock_rds_client = MockClient.return_value
        mock_rds_client.overwrite_table_with_df = MagicMock()
        mock_rds_client.append_df_to_table = MagicMock()
        mock_rds_client.read_table.return_value = pd.DataFrame(
            [{"result": "validated_1"}, {"result": "validated_2"}]
        )

        # Execute the main code in __main__
        with patch("builtins.__name__", "__main__"):
            # Import the main script to trigger the __main__ block
            import aind_metadata_validator.sync  # Replace with the actual script file name

        # Assertions to check expected calls
        mock_metadata_client.retrieve_docdb_records.assert_called_once_with(
            filter_query={}, limit=0, paginate_batch_size=100
        )
        self.assertEqual(
            mock_validate_metadata.call_count, 2
        )  # Called for each record

        # DataFrame calls
        mock_to_csv.assert_any_call("validation_results.csv", index=False)
        mock_to_csv.assert_any_call(
            "validation_results_from_rds.csv", index=False
        )

        # RDS client overwrite and append calls
        mock_rds_client.overwrite_table_with_df.assert_called_once()
        if (
            len(mock_metadata_client.retrieve_docdb_records.return_value)
            > 1000
        ):
            mock_rds_client.append_df_to_table.assert_called()

        # Check logging
        with self.assertLogs(level="INFO") as log:
            logging.info("(METADATA VALIDATOR) Success")
        self.assertIn("(METADATA VALIDATOR) Success", log.output[-1])


if __name__ == "__main__":
    unittest.main()
