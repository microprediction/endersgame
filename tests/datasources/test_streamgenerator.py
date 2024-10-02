import pytest
from unittest.mock import patch, MagicMock
from endersgame.datasources.streamgenerator import stream_generator


class TestStreamGenerator:
    @patch('requests.get')
    def test_stream_generator_normal(self, mock_get):
        """
        Test the generator with two CSV files containing values.
        """
        # Simulate CSV content for two files
        csv_content_file_1 = "value\n1.0\n2.0\n3.0\n"
        csv_content_file_2 = "value\n4.0\n5.0\n"

        # Define side effects for requests.get to return different content based on URL
        def side_effect(url):
            if "stream_0_file_1.csv" in url:
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.content = csv_content_file_1.encode('utf-8')
                return mock_resp
            elif "stream_0_file_2.csv" in url:
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.content = csv_content_file_2.encode('utf-8')
                return mock_resp
            else:
                # Simulate no more files (HTTP 404)
                mock_resp = MagicMock()
                mock_resp.status_code = 404
                return mock_resp

        mock_get.side_effect = side_effect

        # Instantiate the generator
        gen = stream_generator(stream_id=0, category='train', return_float=True)
        # Collect all values from the generator
        results = list(gen)
        expected_results = [1.0, 2.0, 3.0, 4.0, 5.0]

        assert results == expected_results

    @patch('requests.get')
    def test_empty_file(self, mock_get):
        """
        Test the generator when an empty CSV file is encountered.
        """
        csv_content_empty = ""

        def side_effect(url):
            if "stream_0_file_1.csv" in url:
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.content = csv_content_empty.encode('utf-8')
                return mock_resp
            else:
                mock_resp = MagicMock()
                mock_resp.status_code = 404
                return mock_resp

        mock_get.side_effect = side_effect

        gen = stream_generator(stream_id=0, category='train', return_float=True)
        results = list(gen)
        expected_results = []

        assert results == expected_results


    @patch('requests.get')
    def test_no_files_available(self, mock_get):
        """
        Test the generator when no files are available (all requests return 404).
        """
        def side_effect(url):
            mock_resp = MagicMock()
            mock_resp.status_code = 404
            return mock_resp

        mock_get.side_effect = side_effect

        gen = stream_generator(stream_id=0, category='train', return_float=True)
        results = list(gen)
        expected_results = []

        assert results == expected_results

    @patch('requests.get')
    def test_error_handling(self, mock_get):
        """
        Test the generator's handling of network errors.
        """
        import requests
        def side_effect(url):
            raise requests.exceptions.ConnectionError("Network error")

        mock_get.side_effect = side_effect

        gen = stream_generator(stream_id=0, category='train', return_float=True)
        results = list(gen)
        expected_results = []

        assert results == expected_results
