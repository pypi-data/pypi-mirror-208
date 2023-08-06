
import os.path
import unittest

from tinybird.csv_guess import guess_delimiter, guess_columns, has_header
from tinybird.csv_processing_queue import MAX_GUESS_BYTES, cut_csv_extract
from .utils import fixture_data


class TestCSVGuessDelimiter(unittest.TestCase):

    def test_csv_delimiter(self):
        data = fixture_data('movies.csv')
        delimiter = guess_delimiter(data)
        self.assertEqual(delimiter, ';')

    def test_csv_fact_venta_delimiter(self):
        data = fixture_data('fact_venta.csv')
        delimiter = guess_delimiter(data)
        self.assertEqual(delimiter, ',')

    def test_another_csv_delimiter(self):
        data = fixture_data('salas.csv')
        delimiter = guess_delimiter(data)
        self.assertEqual(delimiter, ';')

    def test_guess_float_column(self):
        data = fixture_data('float_column.csv')
        column_types = guess_columns(data, ',')

        guessed_types = [x['type'] for x in column_types]
        self.assertEqual(['Int64', 'Int64', 'Int64', 'Float32'], guessed_types)

    def test_guess_float_column_taxi(self):
        data = cut_csv_extract(fixture_data('float_column_taxi.csv')[:MAX_GUESS_BYTES], MAX_GUESS_BYTES)
        column_types = guess_columns(data, ',')

        guessed_types = [x['type'] for x in column_types]
        # last column is detected as String because they are all nulls
        actual_types = ['Int16', 'DateTime', 'DateTime', 'Int16', 'Float32', 'Int16', 'String', 'Int32', 'Int32', 'Int16', 'Float32', 'Float32', 'Float32', 'Float32', 'Float32', 'Float32', 'Float32', 'String']
        self.assertEqual(actual_types, guessed_types)

    def test_guess_float_column_with_string_as_string(self):
        data = fixture_data('float_column_with_string.csv')
        column_types = guess_columns(data, ',')

        guessed_types = [x['type'] for x in column_types]
        self.assertEqual(['Int64', 'Int64', 'Int64', 'String'], guessed_types)

    def test_has_header(self):
        with_headers = [
            "messy_headers.csv",
            "yt_1000.csv",
            "2918c.csv",
            "spanish_dates_0.csv",
            "small.csv",
            "yt_100.csv",
            "yt_1000_table_in_column.csv",
            "salas.csv",
            "parsing_error.csv",
            "bad_header.csv",
            "trans.csv",
            "shopify_export.csv",
            "CEND_14_13.csv",
            "float_column_with_string.csv",
            "float_column_taxi.csv",
            "tweet_activity_metrics_javisantana_20190220_20190320_en.csv",
            "arrays.csv",
            "movies.csv",
            "dates_with_decimals.csv",
            "sales_0.csv",
            "float_column.csv",
            "sales_1.csv",
            "sales_3.csv",
            "sales_2.csv",
        ]
        for file in with_headers:
            print(f"file with headers: {file}")
            data = fixture_data(os.path.basename(file))
            hh, _, _ = has_header(data, guess_delimiter(data))
            self.assertTrue(hh)

    def test_stop_iteration_exception(self):
        data = fixture_data('too_many_blank_lines.csv')
        column_types = guess_columns(data, ',')

        guessed_types = [x['type'] for x in column_types]
        expected_guessed_types = ['DateTime64', 'String', 'String']

        self.assertEqual(expected_guessed_types, guessed_types)

    def test_no_has_header(self):
        with_no_headers = [
            ("issue-920.csv", ','),
            ("issue-920-b.csv", ','),
        ]
        for (file, expected_delimiter) in with_no_headers:
            data = fixture_data(os.path.basename(file))
            delimiter = guess_delimiter(data)
            self.assertEqual(delimiter, expected_delimiter)
            hh, _, _ = has_header(data, delimiter)
            self.assertFalse(hh)


if __name__ == '__main__':
    unittest.main()
