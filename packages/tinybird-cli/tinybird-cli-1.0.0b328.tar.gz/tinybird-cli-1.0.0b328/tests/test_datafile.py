
import os
import unittest

import click

from tinybird.datafile import parse, ValidationException, ParseException


class TestDatafile(unittest.TestCase):

    def setUp(self):
        super().setUp()

    def test_parse_version(self):
        s = """
        VERSION 10
        """
        doc = parse(s)
        self.assertEqual(doc.version, 10)

    def test_parse_wrong_version(self):
        s = """
        VERSION -1
        """
        with self.assertRaises(ValidationException):
            parse(s)

    def test_general_parse(self):
        s = """
FROM SCRATCH
SOURCE 'https://example.com'
# this is a comment
MAINTAINER 'rambo' # this is me
NODE test_01
DESCRIPTION this is a node that does whatever
SQL >
  SELECT * from test_00

NODE test_02
SQL >
   SELECT * from test_01
   WHERE a > 1
   GROUP by a
        """
        d = parse(s)
        self.assertEqual(d.maintainer, 'rambo')
        self.assertEqual(len(d.nodes), 2, d.nodes)
        self.assertEqual(d.nodes[0], {
            'name': 'test_01',
            'description': 'this is a node that does whatever', 'sql': 'SELECT * from test_00'
        })
        self.assertEqual(d.nodes[1], {'name': 'test_02', 'sql': 'SELECT * from test_01\nWHERE a > 1\nGROUP by a'})

    def test_pipe_description_parse(self):
        content = """
DESCRIPTION >
    This is the main pipe description
NODE test_01
DESCRIPTION this is the first node description
SQL >
    SELECT * from test_00
        """
        pipe = parse(content)
        self.assertEqual(pipe.description, 'This is the main pipe description')
        self.assertEqual(len(pipe.nodes), 1, pipe.nodes)

    def test_datasource_description_parse(self):
        content = """
DESCRIPTION >
    This is the main datasource description
        """
        datasource = parse(content, 'default')
        self.assertEqual(datasource.nodes[0]['description'], 'This is the main datasource description')

    def test_datasource_engine(self):
        s = """VERSION 0
SCHEMA >
    a Date,
    b Float32,
    c String

ENGINE "MergeTree"
ENGINE_PARTITION_KEY "toYYYYMM(a)"
ENGINE_SORTING_KEY "(c, a)"
        """
        ds = parse(s, 'default')
        self.assertIn('engine', ds.nodes[0])
        self.assertEqual(ds.nodes[0]['engine']['type'], 'MergeTree')
        self.assertEqual(ds.nodes[0]['engine']['args'], [('partition_key', 'toYYYYMM(a)'), ('sorting_key', '(c, a)')])

    def test_parse_engine_no_node(self):
        s = """
        ENGINE "MergeTree"
        """
        with self.assertRaisesRegex(Exception, "ENGINE must be called after a NODE command"):
            parse(s)

        s = """
        ENGINE_PARTITION_KEY "toYYYYMM(a)"
        """
        with self.assertRaisesRegex(Exception, "ENGINE_PARTITION_KEY must be called after a NODE command"):
            parse(s)

    def test_node_engine(self):
        s = """VERSION 0
NODE mat_node
SQL >
    SELECT toDate(ts) as date, country, sum(sales) sum_sales FROM ds

DATASOURCE "daily_sales_by_country"
ENGINE "SummingMergeTree"
ENGINE_PARTITION_KEY "toYYYYMM(date)"
ENGINE_SORTING_KEY "(country, date)"
ENGINE_SETTINGS "index_granularity=32"
ENGINE_TTL "toDate(date) + INTERVAL 3 DAY"
        """
        ds = parse(s)
        self.assertIn('engine', ds.nodes[0])
        self.assertEqual(ds.nodes[0]['engine']['type'], 'SummingMergeTree')
        self.assertEqual(ds.nodes[0]['engine']['args'], [('partition_key', 'toYYYYMM(date)'), ('sorting_key', '(country, date)'), ('settings', 'index_granularity=32'), ('ttl', 'toDate(date) + INTERVAL 3 DAY')])
        self.assertEqual(ds.nodes[0]['datasource'], 'daily_sales_by_country')

    def test_no_indentation_parse(self):
        s = """VERSION 0
NODE mat_node
SQL >
SELECT toDate(ts) as date, country, sum(sales) sum_sales FROM ds

DATASOURCE "daily_sales_by_country"
ENGINE "SummingMergeTree"
ENGINE_PARTITION_KEY "toYYYYMM(date)"
ENGINE_SORTING_KEY "(country, date)"
ENGINE_SETTINGS "index_granularity=32"
ENGINE_TTL "toDate(date) + INTERVAL 3 DAY"
        """
        ds = parse(s)
        self.assertIn('engine', ds.nodes[0])
        self.assertEqual(ds.nodes[0]['sql'], 'SELECT toDate(ts) as date, country, sum(sales) sum_sales FROM ds')
        self.assertEqual(ds.nodes[0]['engine']['type'], 'SummingMergeTree')
        self.assertEqual(ds.nodes[0]['engine']['args'], [('partition_key', 'toYYYYMM(date)'), ('sorting_key', '(country, date)'), ('settings', 'index_granularity=32'), ('ttl', 'toDate(date) + INTERVAL 3 DAY')])
        self.assertEqual(ds.nodes[0]['datasource'], 'daily_sales_by_country')

    def test_no_indentation_multiline_parse(self):
        s = """VERSION 0
NODE mat_node
SQL >
SELECT toDate(ts) as date,
country,
sum(sales) sum_sales
FROM ds

DATASOURCE "daily_sales_by_country"
ENGINE "SummingMergeTree"
ENGINE_PARTITION_KEY "toYYYYMM(date)"
ENGINE_SORTING_KEY "(country, date)"
ENGINE_SETTINGS "index_granularity=32"
ENGINE_TTL "toDate(date) + INTERVAL 3 DAY"
        """
        ds = parse(s)
        self.assertIn('engine', ds.nodes[0])
        self.assertEqual(ds.nodes[0]['sql'], 'SELECT toDate(ts) as date,\ncountry,\nsum(sales) sum_sales\nFROM ds')
        self.assertEqual(ds.nodes[0]['engine']['type'], 'SummingMergeTree')
        self.assertEqual(ds.nodes[0]['engine']['args'], [('partition_key', 'toYYYYMM(date)'), ('sorting_key', '(country, date)'), ('settings', 'index_granularity=32'), ('ttl', 'toDate(date) + INTERVAL 3 DAY')])
        self.assertEqual(ds.nodes[0]['datasource'], 'daily_sales_by_country')

    def test_no_indentation_multiline_group_parse(self):
        s = """VERSION 0
NODE mat_node
SQL >
SELECT toDate(ts) as date,
country,
sum(sales) sum_sales
FROM ds
GROUP BY date
country

DATASOURCE "daily_sales_by_country"
ENGINE "SummingMergeTree"
ENGINE_PARTITION_KEY "toYYYYMM(date)"
ENGINE_SORTING_KEY "(country, date)"
ENGINE_SETTINGS "index_granularity=32"
ENGINE_TTL "toDate(date) + INTERVAL 3 DAY"
        """
        ds = parse(s)
        self.assertIn('engine', ds.nodes[0])
        self.assertEqual(ds.nodes[0]['sql'], 'SELECT toDate(ts) as date,\ncountry,\nsum(sales) sum_sales\nFROM ds\nGROUP BY date\ncountry')
        self.assertEqual(ds.nodes[0]['engine']['type'], 'SummingMergeTree')
        self.assertEqual(ds.nodes[0]['engine']['args'], [('partition_key', 'toYYYYMM(date)'), ('sorting_key', '(country, date)'), ('settings', 'index_granularity=32'), ('ttl', 'toDate(date) + INTERVAL 3 DAY')])
        self.assertEqual(ds.nodes[0]['datasource'], 'daily_sales_by_country')

    def test_no_indentation_multiline_with_validation_error_parse(self):
        s = """VERSION 0
NODE mat_node
SQL >
SELECT toDate(ts) as date, country, sum(sales) sum_sales FROM test
as

DATASOURCE
where date = '2020-01-01'

DATASOURCE "test"
        """
        with self.assertRaises(click.ClickException) as ctx:
            parse(s)
        self.assertTrue('Missing datasource name for pipe creation after the DATASOURCE label' in str(ctx.exception))

    def test_no_indentation_multiline_with_parse_error(self):
        s = """VERSION 0
NODE mat_node
SQL >
SELECT toDate(ts) as date, country, sum(sales) sum_sales FROM test
as

DATASOURCE "test"
where date = '2020-01-01'
        """
        with self.assertRaises(ParseException) as ctx:
            parse(s)
        self.assertIn('WHERE is not a valid option', str(ctx.exception))

    def test_read_env_vars(self):
        s = """VERSION 0
NODE "mat_${test}"

SQL >
SELECT toDate(ts) as date,
country,
sum(sales) sum_sales
FROM ds
GROUP BY date
country

DATASOURCE "${test}_ds"
ENGINE "SummingMergeTree${doesnotexist}"
        """
        os.environ['test'] = 'rambo'
        ds = parse(s)
        self.assertIn('datasource', ds.nodes[0])
        self.assertEqual(ds.nodes[0]['datasource'], 'rambo_ds')
        self.assertEqual(ds.nodes[0]['name'], 'mat_rambo')
        self.assertEqual(ds.nodes[0]['engine']['type'], 'SummingMergeTree${doesnotexist}')

    def test_parse_bigquery_datasource_import(self):
        content = """
DESCRIPTION >
    Test

SCHEMA >
    `Year` Nullable(Int64),
    `Industry_aggregation_NZSIOC` Nullable(String),
    `Industry_code_NZSIOC` Nullable(String),
    `Industry_name_NZSIOC` Nullable(String),
    `Units` Nullable(String),
    `Variable_code` Nullable(String),
    `Variable_name` Nullable(String),
    `Variable_category` Nullable(String),
    `Value` Nullable(String),
    `Industry_code_ANZSIC06` Nullable(String)

ENGINE "MergeTree"
ENGINE_PARTITION_KEY "toYear(insertion_date)"
ENGINE_SORTING_KEY "insertion_date"

IMPORT_SERVICE bigquery
IMPORT_SCHEDULE "*/25 * * * *"
IMPORT_STRATEGY replace
IMPORT_QUERY >
    SELECT * FROM avid-atlas-375013.test_data.test_table
        """
        ds = parse(content, 'test')

        node = ds.nodes[0]
        self.assertEqual(node['import_service'], 'bigquery')
        self.assertEqual(node['import_schedule'], '*/25 * * * *')
        self.assertEqual(node['import_strategy'], 'replace')
        self.assertEqual(node['import_query'].strip(), 'SELECT * FROM avid-atlas-375013.test_data.test_table')

    def test_parse_swnowflake_datasource_import(self):
        content = """
DESCRIPTION >
    Test

SCHEMA >
    `O_ORDERKEY` Nullable(Int64),
    `O_CUSTKEY` Nullable(Int64)

ENGINE "MergeTree"
ENGINE_PARTITION_KEY "toYear(insertion_date)"
ENGINE_SORTING_KEY "insertion_date"

IMPORT_CONNECTION_NAME "sf_connection"
IMPORT_EXTERNAL_DATA_SOURCE "TINYBIRD.SAMPLES.ORDERS_1M"
IMPORT_SERVICE "snowflake"
IMPORT_SCHEDULE "*/25 * * * *"
IMPORT_STRATEGY "replace"
IMPORT_QUERY "SELECT O_ORDERKEY, O_CUSTKEY FROM TINYBIRD.SAMPLES.ORDERS_1M"
        """
        ds = parse(content, 'test')

        node = ds.nodes[0]
        self.assertEqual(node['import_connection_name'], 'sf_connection')
        self.assertEqual(node['import_external_data_source'], 'TINYBIRD.SAMPLES.ORDERS_1M')
        self.assertEqual(node['import_service'], 'snowflake')
        self.assertEqual(node['import_schedule'], '*/25 * * * *')
        self.assertEqual(node['import_strategy'], 'replace')
        self.assertEqual(node['import_query'].strip(), 'SELECT O_ORDERKEY, O_CUSTKEY FROM TINYBIRD.SAMPLES.ORDERS_1M')

    def test_parse_datasource_import_strip_query(self):
        content = """
DESCRIPTION >
    Test

SCHEMA >
    `Year` Nullable(Int64)

ENGINE "MergeTree"
ENGINE_PARTITION_KEY "toYear(insertion_date)"
ENGINE_SORTING_KEY "insertion_date"

IMPORT_SERVICE bigquery
IMPORT_SCHEDULE "*/25 * * * *"
IMPORT_STRATEGY replace
IMPORT_QUERY 'SELECT * FROM avid-atlas-375013.test_data.test_table'
        """
        ds = parse(content, 'test')

        node = ds.nodes[0]
        self.assertEqual(node['import_query'].strip(), 'SELECT * FROM avid-atlas-375013.test_data.test_table')

    def test_parse_datasource_import_strip_multiline_query(self):
        content = """
DESCRIPTION >
    Test

SCHEMA >
    `Year` Nullable(Int64)

ENGINE "MergeTree"
ENGINE_PARTITION_KEY "toYear(insertion_date)"
ENGINE_SORTING_KEY "insertion_date"

IMPORT_SERVICE bigquery
IMPORT_SCHEDULE "*/25 * * * *"
IMPORT_STRATEGY replace
IMPORT_QUERY >
    'SELECT * FROM avid-atlas-375013.test_data.test_table'
        """
        ds = parse(content, 'test')

        node = ds.nodes[0]
        self.assertEqual(node['import_query'].strip(), 'SELECT * FROM avid-atlas-375013.test_data.test_table')
