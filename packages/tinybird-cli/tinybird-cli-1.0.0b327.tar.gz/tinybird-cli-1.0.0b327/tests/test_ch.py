import asyncio
from chtoolset import query as chquery
from collections import Counter
import json
import threading
import time
import uuid
import zlib
import unittest

from functools import partial
from http.server import SimpleHTTPRequestHandler, HTTPServer
from io import BytesIO
from socketserver import ThreadingMixIn
from unittest.mock import Mock, call, patch, ANY

import requests
from tests.conftest import CH_ADDRESS, OTHER_STORAGE_POLICY, DEFAULT_CLUSTER
from tinybird.constants import CHCluster

from tinybird.syncasync import async_to_sync
from tinybird.sql import parse_table_structure
from tinybird.user import User, UserAccount
from tinybird.app import global_patch_for_requests_timeout
from tinybird.ch import (
    ch_create_exact_empty_copy, ch_guarded_query as _ch_guarded_query,
    HTTPClient, ch_table_details_async, ch_truncate_table,
    ch_truncate_table_with_fallback,
    url_from_host, ch_table_partitions_sync,
    ch_wait_for_query_cancellation, WaitingCancelOperationResult,
    table_structure, CHTable, ch_describe_query,
    ch_get_columns_from_query, CSVInfo, ch_table_dependent_views_sync,
    CHTableLocation, ch_table_partitions_for_sample_sync,
    _get_query_log, ch_flush_logs_on_all_replicas, ch_get_cluster_instances,
    ch_flush_logs_on_all_replicas_sync, ch_attach_partitions, ch_query_table_partitions, Partitions,
    ch_estimate_query_rows, CHReplication)
from tinybird.csv_tools import csv_from_python_object
from tinybird.ch_utils.exceptions import CHException
from tinybird.ch_utils.errors import CHErrors

ch_guarded_query = partial(_ch_guarded_query, check_frequency_seconds=.05)
sync_ch_describe_query = async_to_sync(ch_describe_query)


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    first_query_log_query = True


class ProxyHandler(SimpleHTTPRequestHandler):
    def __init__(self, database_server, *args, **kwargs):
        self.upstream_server = url_from_host(database_server)[:-1]
        super().__init__(*args, **kwargs)

    def log_message(self, *args, **kwargs):
        pass

    def do_GET(self):
        if self.server.first_query_log_query and 'fail_first_query_log_query' in self.path:
            self.server.first_query_log_query = False
            self.send_response(500)
            self.end_headers()
            self.copyfile(BytesIO('Code: 160, e.displayText() = DB::Exception: Estimated query execution time (22.506430934551624 seconds) is too long. Maximum: 10. Estimated rows to process: 159418181: While executing MergeTreeThread (version 20.7.2.30 (official build))'.encode()), self.wfile)
            return
        r = requests.get(f"{self.upstream_server}{self.path}")
        self.send_response(r.status_code)
        self.end_headers()
        self.copyfile(BytesIO(r.content), self.wfile)

    def do_POST(self):
        query_length = int(self.headers.get('Content-Length', 0))
        query = self.rfile.read(query_length)
        try:
            # timeout=(0.5, 0.5)
            # We could define a timeout to better emulate the Varnish behaviour.
            # However, requests close the connection to the actual ClickHouse server
            # and that makes ClickHouse unhappy, logging an error about not being able
            # to write to the output stream.
            _ = requests.post(f"{self.upstream_server}{self.path}", data=query)
            # self.send_response(r.status_code)
            # self.end_headers()
            # self.copyfile(BytesIO(r.content), self.wfile)
        finally:
            self.send_response(503)
            self.end_headers()


class TestGuardedQueries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        WORKSPACE = f'test_ch_{uuid.uuid4().hex}'
        USER = f'{WORKSPACE}@example.com'

        cls.user = UserAccount.register(USER, 'pass')
        cls.workspace = User.register(WORKSPACE, cls.user.id, DEFAULT_CLUSTER)
        client = HTTPClient(cls.workspace.database_server, database=None)
        client.query_sync(f"CREATE DATABASE IF NOT EXISTS {cls.workspace.database} ON CLUSTER tinybird", read_only=False)

    @classmethod
    def tearDownClass(cls):
        database = cls.workspace.database
        client = HTTPClient(cls.workspace.database_server, database=None)
        User._delete(cls.workspace.id)
        UserAccount._delete(cls.user.id)
        client.query_sync(f"DROP DATABASE IF EXISTS `{database}` ON CLUSTER tinybird SYNC", read_only=False)
        super().tearDownClass()

    def test_query_ok(self):
        query = "SELECT 1"
        query_id, query_finish = ch_guarded_query(self.workspace.database_server, self.workspace.database, query, 'tinybird')
        self.assertIsNotNone(query_id)
        self.assertIsNotNone(query_finish)

    def test_query_error(self):
        query = "SELECT faulty query"
        with self.assertRaisesRegex(CHException, r"Missing columns: 'faulty'"):
            ch_guarded_query(self.workspace.database_server, self.workspace.database, query, 'tinybird')

    def test_query_max_execution_time(self):
        query = "SELECT sleepEachRow(1) FROM numbers(3)"
        with self.assertRaisesRegex(CHException, r"Timeout exceeded"):
            ch_guarded_query(self.workspace.database_server, self.workspace.database, query, 'tinybird', max_execution_time=1)

    def test_varnish_behaviour(self):
        query = "SELECT sleep(0.01)"
        query_id, query_finish = ch_guarded_query(CH_ADDRESS, self.workspace.database, query, 'tinybird')
        self.assertIsNotNone(query_id)
        self.assertIsNotNone(query_finish)

    def test_query_ok_with_failure_on_check(self):
        query = "SELECT 1"
        query_id, query_finish = ch_guarded_query(CH_ADDRESS, self.workspace.database, query, 'tinybird',
                                                  query_id="fail_first_query_log_query")
        self.assertIsNotNone(query_id)
        self.assertIsNotNone(query_finish)

    def test_query_directly_returns_if_externally_cancelled(self):

        externally_cancelled_function = Mock(return_value=True)

        query = "SELECT sleep(3)"
        query_id, query_finish = ch_guarded_query(
            self.workspace.database_server, self.workspace.database, query, 'tinybird',
            query_id="random_query_id", has_been_externally_cancelled=externally_cancelled_function)
        self.assertIsNotNone(query_id)
        self.assertIsNone(query_finish)

    def test_query_returns_after_the_query_is_made_if_externally_cancelled(self):

        externally_cancelled_function = Mock(side_effect=[False, True, True])

        query = "SELECT sleep(0.01)"
        query_id, query_finish = ch_guarded_query(
            self.workspace.database_server, self.workspace.database, query, 'tinybird', query_id="random_query_id",
            has_been_externally_cancelled=externally_cancelled_function)
        self.assertIsNotNone(query_id)
        self.assertIsNone(query_finish)
        externally_cancelled_function.assert_has_calls([call()] * 2)


class TestPartitions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        WORKSPACE = f'test_ch_{uuid.uuid4().hex}'
        USER = f'{WORKSPACE}@example.com'
        cls.user = UserAccount.register(USER, 'pass')
        cls.workspace = User.register(WORKSPACE, cls.user.id, CHCluster(name='tinybird', server_url=CH_ADDRESS))
        client = HTTPClient(cls.workspace.database_server, database=None)
        client.query_sync(f"CREATE DATABASE IF NOT EXISTS {cls.workspace.database} ON CLUSTER tinybird", read_only=False)

    @classmethod
    def tearDownClass(cls):
        client = HTTPClient(cls.workspace.database_server, database=None)
        database = cls.workspace.database
        User._delete(cls.workspace.id)
        UserAccount._delete(cls.user.id)
        client.query_sync(f"DROP DATABASE IF EXISTS {database} ON CLUSTER tinybird", read_only=False)
        super().tearDownClass()

    def _create_table(self, name, schema, partition_key, data_sql, engine: str = 'MergeTree'):
        client = HTTPClient(self.workspace.database_server, database=self.workspace.database)
        full_engine = f"Replicated{engine}('/clickhouse/tables/{{layer}}-{{shard}}/{self.workspace.database}.{name}','{{replica}}')"
        create_sql = f'''CREATE TABLE {name} ON CLUSTER tinybird ({schema})
            ENGINE = {full_engine}
            PARTITION BY {partition_key}
            ORDER BY tuple()'''
        client.query_sync(create_sql, read_only=False)
        if data_sql:
            client.query_sync(f"INSERT INTO {name} {data_sql}", read_only=False)

    def test_ch_partitions_tuple(self):
        schema = 'a String, b DateTime'
        partition_key = 'tuple()'
        data_sql = """SELECT
            'a' as a,
            now() as b
        FROM numbers(10)"""
        self._create_table("test_ch_partitions_tuple", schema, partition_key, data_sql)

        partitions = ch_table_partitions_sync(self.workspace.database_server, self.workspace.database, ["test_ch_partitions_tuple"])
        self.assertEqual(partitions, ['tuple()'])

    def test_ch_partitions_date(self):
        schema = 'a String, b DateTime'
        partition_key = 'toDate(b)'
        data_sql = """SELECT
            'a' as a,
            toDateTime('2020-12-01 00:00:00') + INTERVAL number DAY as b
        FROM numbers(5)"""
        self._create_table("test_ch_partitions_date", schema, partition_key, data_sql)

        partitions = ch_table_partitions_sync(self.workspace.database_server, self.workspace.database, ["test_ch_partitions_date"])
        self.assertEqual(
            partitions,
            ["'2020-12-05'", "'2020-12-04'", "'2020-12-03'", "'2020-12-02'", "'2020-12-01'"]
        )

    def test_ch_partitions_subset(self):
        schema = 'a String, b DateTime'
        partition_key = 'substring(a, 1, 1)'
        data_sql = """SELECT
            toString(number) as a,
            now() as b
        FROM numbers(1000)"""
        self._create_table("test_ch_partitions_subset", schema, partition_key, data_sql)

        partitions = ch_table_partitions_for_sample_sync(self.workspace.database_server, self.workspace.database, "test_ch_partitions_subset", max_rows=10)
        self.assertEqual(len(partitions), 1)
        # least(1000 * 0.1, 10) => 10
        self.assertEqual(partitions[0][1], 10)

    def test_ch_partitions_yyyymm(self):
        schema = 'a String, b DateTime'
        partition_key = 'toYYYYMM(b)'
        data_sql = """SELECT
            'a' as a,
            toDateTime('2020-12-01 00:00:00') + INTERVAL number DAY as b
        FROM numbers(90)"""
        self._create_table("test_ch_partitions_yyyymm", schema, partition_key, data_sql)

        partitions = ch_table_partitions_sync(self.workspace.database_server, self.workspace.database, ["test_ch_partitions_yyyymm"])
        self.assertEqual(partitions, ['202102', '202101', '202012'])

    def test_ch_partitions_numeric(self):
        schema = 'n Int8, b DateTime'
        partition_key = 'n % 5'
        data_sql = """SELECT
            number as n,
            toDateTime('2020-12-01 00:00:00') + INTERVAL number DAY as b
        FROM numbers(25)"""
        self._create_table("test_ch_partitions_numeric", schema, partition_key, data_sql)

        partitions = ch_table_partitions_sync(self.workspace.database_server, self.workspace.database, ["test_ch_partitions_numeric"])
        self.assertEqual(partitions, ['4', '3', '2', '1', '0'])

    def test_ch_partitions_two_partition_keys(self):
        schema = 'a String, b DateTime'
        partition_key = '(a, toYYYYMM(b))'
        data_sql = """SELECT
            if(number % 2 = 0, 'a', 'b') as a,
            toDateTime('2020-12-01 00:00:00') + INTERVAL number DAY as b
        FROM numbers(90)"""
        self._create_table("test_ch_partitions_two_partition_keys", schema, partition_key, data_sql)

        partitions = ch_table_partitions_sync(self.workspace.database_server, self.workspace.database, ["test_ch_partitions_two_partition_keys"])
        self.assertEqual(
            Counter(partitions),
            Counter(["('b',202102)", "('b',202101)", "('b',202012)", "('a',202102)", "('a',202101)", "('a',202012)"])
        )

    def test_ch_partitions_datetime(self):
        schema = 'a String, b DateTime'
        partition_key = 'b'
        data_sql = """SELECT
            'a' as a,
            toDateTime('2020-12-01 00:00:00') + INTERVAL number DAY as b
        FROM numbers(3)"""
        self._create_table("test_ch_partitions_datetime", schema, partition_key, data_sql)

        partitions = ch_table_partitions_sync(self.workspace.database_server, self.workspace.database, ["test_ch_partitions_datetime"])
        self.assertEqual(
            partitions,
            ["'2020-12-03 00:00:00'", "'2020-12-02 00:00:00'", "'2020-12-01 00:00:00'"]
        )

    def test_ch_partitions_with_met_condition(self):
        schema = 'a String, b DateTime'
        partition_key = 'toYYYYMM(b)'
        data_sql = """SELECT
            'a' as a,
            toDateTime('2020-12-01 00:00:00') + INTERVAL number DAY as b
        FROM numbers(90)"""
        self._create_table("test_ch_partitions_with_met_condition", schema, partition_key, data_sql)
        condition = "b > toDateTime('2021-01-01 00:00:00') and a = 'a'"
        expected_partitions = ['202102', '202101']

        partitions = ch_table_partitions_sync(self.workspace.database_server, self.workspace.database,
                                              ["test_ch_partitions_with_met_condition"], condition)
        self.assertEqual(partitions, expected_partitions)

    def test_ch_partitions_with_unmet_condition(self):
        schema = 'a String, b DateTime'
        partition_key = 'toYYYYMM(b)'
        data_sql = """SELECT
            'a' as a,
            toDateTime('2020-12-01 00:00:00') + INTERVAL number DAY as b
        FROM numbers(90)"""
        self._create_table("test_ch_partitions_with_unmet_condition", schema, partition_key, data_sql)
        condition = "b > toDateTime('2023-01-01 00:00:00') and a = 'a'"
        expected_partitions = []

        partitions = ch_table_partitions_sync(self.workspace.database_server, self.workspace.database,
                                              ["test_ch_partitions_with_unmet_condition"], condition)
        self.assertEqual(partitions, expected_partitions)

    def test_ch_partitions_with_unknown_column_in_condition(self):
        schema = 'a String, b DateTime'
        partition_key = 'toYYYYMM(b)'
        data_sql = """SELECT
            'a' as a,
            toDateTime('2020-12-01 00:00:00') + INTERVAL number DAY as b
        FROM numbers(90)"""
        self._create_table("test_ch_partitions_with_unknown_column_in_condition", schema, partition_key, data_sql)
        condition = "whatever > toDateTime('2023-01-01 00:00:00')"
        expected_partitions = ['202102', '202101', '202012']

        partitions = ch_table_partitions_sync(self.workspace.database_server, self.workspace.database,
                                              ["test_ch_partitions_with_unknown_column_in_condition"], condition)
        self.assertEqual(partitions, expected_partitions)

    def test_ch_partitions_with_other_table_in_condition(self):
        schema = 'a String, b DateTime'
        partition_key = 'toYYYYMM(b)'
        data_sql = """SELECT
            'a' as a,
            toDateTime('2020-12-01 00:00:00') + INTERVAL number DAY as b
        FROM numbers(90)"""
        self._create_table("test_ch_partitions_with_other_table_in_condition", schema, partition_key, data_sql)

        other_table = 'other_table'
        other_engine = f"ReplicatedMergeTree('/clickhouse/tables/{{layer}}-{{shard}}/{self.workspace.database}.{other_table}','{{replica}}')"
        create_sql = f'''CREATE TABLE {other_table} ON CLUSTER tinybird (a String, b DateTime) ENGINE = {other_engine} ORDER BY b'''
        client = HTTPClient(self.workspace.database_server, database=self.workspace.database)
        client.query_sync(create_sql, read_only=False)
        data_sql = """SELECT
            'a' as a,
            toDateTime('2021-01-01 00:00:00') + INTERVAL number DAY as b
        FROM numbers(90)"""
        client.query_sync(f"INSERT INTO {other_table} {data_sql}", read_only=False)
        condition = f"b > (SELECT min(b) FROM {self.workspace.database}.{other_table})"

        expected_partitions = ['202102', '202101']

        partitions = ch_table_partitions_sync(self.workspace.database_server, self.workspace.database,
                                              ["test_ch_partitions_with_other_table_in_condition"], condition)
        self.assertEqual(partitions, expected_partitions)

    @patch('tinybird.ch._query_table_partitions_with_condition_fallback_sync')
    def test_ch_partitions_for_views(self, mocked_partition_query):
        # The partition query should not be called for Views.
        # Views are not supported on the product, and this is only needed because of the usage of Views on ITX.
        test_name = f'test_ch_partitions_for_views_{uuid.uuid4().hex}'
        table_name, view_name = f'{test_name}_table', f'{test_name}_view'

        schema = 'a String, b DateTime'
        partition_key = 'toYYYYMM(b)'
        data_sql = """SELECT
            'a' as a,
            toDateTime('2020-12-01 00:00:00') + INTERVAL number DAY as b
        FROM numbers(90)"""
        self._create_table(table_name, schema, partition_key, data_sql, engine='ReplacingMergeTree')

        client = HTTPClient(self.workspace.database_server, database=self.workspace.database)
        create_sql = f'''
        CREATE VIEW IF NOT EXISTS {test_name} ON CLUSTER tinybird ({schema})
        AS SELECT * FROM {table_name}'''
        client.query_sync(create_sql, read_only=False)

        partitions = ch_table_partitions_sync(self.workspace.database_server, self.workspace.database, [view_name])
        self.assertEqual(partitions, [])
        condition = "b > toDateTime('2021-01-01 00:00:00') and a = 'a'"
        partitions = ch_table_partitions_sync(self.workspace.database_server, self.workspace.database, [view_name], condition)
        self.assertEqual(partitions, [])

        mocked_partition_query.assert_not_called()

    def test_ch_attach_string_partitions(self):
        schema = 'a String'
        partition_key = 'substring(a, 1, 1)'
        self._create_table("test_ch_partitions_substring", schema, partition_key, None)
        self._create_table("test_ch_partitions_substring2", schema, partition_key, None)
        client = HTTPClient(self.workspace.database_server, database=self.workspace.database)
        client.query_sync("INSERT INTO test_ch_partitions_substring values(' test')", read_only=False)
        client.query_sync("INSERT INTO test_ch_partitions_substring values('(')", read_only=False)
        client.query_sync("INSERT INTO test_ch_partitions_substring values(')')", read_only=False)
        # uncomment after we are in CH 22
        # client.query_sync("INSERT INTO test_ch_partitions_substring values('123')", read_only=False)
        client.query_sync("INSERT INTO test_ch_partitions_substring values('.-')", read_only=False)
        client.query_sync("INSERT INTO test_ch_partitions_substring values('/')", read_only=False)
        client.query_sync("INSERT INTO test_ch_partitions_substring values('''')", read_only=False)

        partitions = async_to_sync(ch_query_table_partitions)(self.workspace.database_server, [self.workspace.database])
        partitions = [p for p in partitions if p.table == 'test_ch_partitions_substring']
        partitions = Partitions().as_sql_list(partitions)
        _, result = async_to_sync(ch_attach_partitions)(self.workspace.database_server, self.workspace.database, "test_ch_partitions_substring2", "test_ch_partitions_substring", partitions)
        self.assertEqual(result, b'')

        schema = 'a String'
        partition_key = 'a'
        self._create_table("test_ch_partitions_substring3", schema, partition_key, None)
        self._create_table("test_ch_partitions_substring4", schema, partition_key, None)
        client = HTTPClient(self.workspace.database_server, database=self.workspace.database)
        client.query_sync("INSERT INTO test_ch_partitions_substring values(' test')", read_only=False)
        client.query_sync("INSERT INTO test_ch_partitions_substring values('.-')", read_only=False)
        client.query_sync("INSERT INTO test_ch_partitions_substring values('/')", read_only=False)
        client.query_sync("INSERT INTO test_ch_partitions_substring values('''')", read_only=False)

        partitions = async_to_sync(ch_query_table_partitions)(self.workspace.database_server, [self.workspace.database])
        partitions = [p for p in partitions if p.table == 'test_ch_partitions_substring']
        partitions = Partitions().as_sql_list(partitions)
        _, result = async_to_sync(ch_attach_partitions)(self.workspace.database_server, self.workspace.database, "test_ch_partitions_substring2", "test_ch_partitions_substring", partitions)
        self.assertEqual(result, b'')

    def test_ch_attach_compound_partitions(self):
        schema = 'a String, b DateTime'
        partition_key = '(toYYYYMM(b), a)'
        self._create_table("test_ch_partitions_compound", schema, partition_key, None)
        self._create_table("test_ch_partitions_compound2", schema, partition_key, None)
        client = HTTPClient(self.workspace.database_server, database=self.workspace.database)
        client.query_sync("INSERT INTO test_ch_partitions_compound values(' test', '2020-01-01 00:00:00')", read_only=False)
        client.query_sync("INSERT INTO test_ch_partitions_compound values('.-', '2021-01-01 00:00:00')", read_only=False)
        client.query_sync("INSERT INTO test_ch_partitions_compound values('/', '2022-01-01 00:00:00')", read_only=False)
        client.query_sync("INSERT INTO test_ch_partitions_compound values('''', '2023-01-01 00:00:00')", read_only=False)

        partitions = async_to_sync(ch_query_table_partitions)(self.workspace.database_server, [self.workspace.database])
        partitions = [p for p in partitions if p.table == 'test_ch_partitions_compound']
        partitions = Partitions().as_sql_list(partitions)
        _, result = async_to_sync(ch_attach_partitions)(self.workspace.database_server, self.workspace.database, "test_ch_partitions_compound2", "test_ch_partitions_compound", partitions)
        self.assertEqual(result, b'')


class TestCancellableQueries(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.database_host = User.default_database_server
        cls.test_database = f'd_cancellable_{uuid.uuid4().hex}'

        ch_client_for_setup = HTTPClient(cls.database_host, database=None)
        ch_client_for_setup.query_sync(f"CREATE DATABASE IF NOT EXISTS {cls.test_database} ON CLUSTER tinybird", read_only=False)

        cls.client = HTTPClient(cls.database_host, database=cls.test_database)

    @classmethod
    def tearDownClass(cls):
        ch_client_for_setup = HTTPClient(cls.database_host, database=None)
        ch_client_for_setup.query_sync(f"DROP DATABASE IF EXISTS {cls.test_database} ON CLUSTER tinybird", read_only=False)
        super().tearDownClass()

    async def test_trying_to_cancel_a_query_that_is_not_actually_running_returns_not_found(self):

        query_id = str(uuid.uuid4())

        result = await ch_wait_for_query_cancellation(
            self.database_host, self.test_database, query_id, 'tinybird', check_frequency_seconds=0.05)

        assert result == WaitingCancelOperationResult.NOT_FOUND

    async def test_trying_to_cancel_a_query_operation_can_finish(self):
        query_id = str(uuid.uuid4())

        def f():
            try:
                self.client.query_sync("SELECT sum(number) FROM numbers(4000000000) settings max_threads = 1;",
                                       query_id=query_id)
            except Exception:
                pass

        self.parallel_thread_to_run_the_query = threading.Thread(target=f)
        self.parallel_thread_to_run_the_query.start()

        await wait_for_query_start(self.client, query_id)

        result = await ch_wait_for_query_cancellation(
            self.database_host, self.test_database, query_id, 'tinybird', wait_seconds=60, check_frequency_seconds=0.05)

        assert result == WaitingCancelOperationResult.CANCELLED or result == WaitingCancelOperationResult.NOT_FOUND


class TestCancellableQueriesBatch2(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.database_host = User.default_database_server
        cls.test_database = f'd_cancellable_{uuid.uuid4().hex}'

        ch_client_for_setup = HTTPClient(cls.database_host, database=None)
        ch_client_for_setup.query_sync(f"CREATE DATABASE IF NOT EXISTS {cls.test_database} ON CLUSTER tinybird", read_only=False)

        cls.client = HTTPClient(cls.database_host, database=cls.test_database)

    @classmethod
    def tearDownClass(cls):
        ch_client_for_setup = HTTPClient(cls.database_host, database=None)
        ch_client_for_setup.query_sync(f"DROP DATABASE IF EXISTS {cls.test_database} ON CLUSTER tinybird", read_only=False)
        super().tearDownClass()

    async def test_trying_to_cancel_a_query_using_async_operation_raise_exception_if_timeout_is_exceeded(self):
        def f():
            try:
                self.client.query_sync("SELECT sleepEachRow(1) from numbers(3);",
                                       query_id=query_id)
            except Exception:
                pass

        query_id = str(uuid.uuid4())
        self.parallel_thread_to_run_the_query = threading.Thread(target=f)
        self.parallel_thread_to_run_the_query.start()

        await wait_for_query_start(self.client, query_id)

        with self.assertRaisesRegex(CHException, r"Timeout exceeded"):
            await ch_wait_for_query_cancellation(self.database_host, self.test_database, query_id, 'tinybird',
                                                 check_frequency_seconds=0.05, wait_seconds=0.01)


class TestStringTableStructureMapping(unittest.TestCase):

    def test_with_different_column_features(self):
        schema = "`simple_column` String, " \
                 "`colummn_with_nullable` Nullable(Int16), " \
                 "`colummn_with_nullable_default_null` Nullable(Int16) DEFAULT NULL, " \
                 "`column_with_default` String DEFAULT 'bla'," \
                 "`column_materialized` String materialized upper(simple_column)"

        columns = parse_table_structure(schema)

        structure = table_structure(columns)

        self.assertEqual("`simple_column` String, "
                         "`colummn_with_nullable` Nullable(Int16), "
                         "`colummn_with_nullable_default_null` Nullable(Int16), "
                         "`column_with_default` String DEFAULT 'bla', "
                         "`column_materialized` String MATERIALIZED upper(simple_column)",
                         structure)

    def test_columns_without_default_value_and_with_name_to_normalize(self):
        columns = [
            {'name': 'my_date_column', 'normalized_name': 'my_date_column', 'type': 'Date', 'nullable': False, 'auto': False, 'default_value': None, 'codec': None},
            {'name': 'other_column', 'normalized_name': 'other_column', 'type': 'Int16', 'nullable': False, 'auto': False, 'default_value': None, 'codec': None}
        ]

        structure = table_structure(columns)

        self.assertEqual("`my_date_column` Date, `other_column` Int16", structure)


class TestCreateTableGeneration(unittest.TestCase):
    def test_generate_create_table_with_nullable_columns(self):

        schema = """
               `no_nullable_string` String,
               `nullable_column` Nullable(Int64),
               `nullable_column_with_default_null` Nullable(Int64) DEFAULT NULL,
               `nullable_column_with_default_cast_null` Nullable(Int64) DEFAULT CAST(NULL, 'Nullable(Int64)'),
               `no_nullable_with_default` String DEFAULT 'bla',
               `no_nullable_with_default_and_cast` String DEFAULT CAST(123, 'String')
            """

        columns = parse_table_structure(schema)

        ch_table = CHTable(columns, cluster='tinybird')

        create_table_statement = ch_table.as_sql("thedatabase", "thetable")
        expected_table_statement = """CREATE TABLE thedatabase.thetable ON CLUSTER tinybird
(
    `no_nullable_string` String,
    `nullable_column` Nullable(Int64),
    `nullable_column_with_default_null` Nullable(Int64),
    `nullable_column_with_default_cast_null` Nullable(Int64) DEFAULT CAST(NULL, 'Nullable(Int64)'),
    `no_nullable_with_default` String DEFAULT 'bla',
    `no_nullable_with_default_and_cast` String DEFAULT CAST(123, 'String')
)
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{layer}-{shard}/thedatabase.thetable', '{replica}')
ORDER BY (no_nullable_string, no_nullable_with_default, no_nullable_with_default_and_cast)"""

        self.assertEqual(chquery.format(expected_table_statement), chquery.format(create_table_statement))  # noqa: W291


class TestSqlAnalysisAndValidations(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.database_host = User.default_database_server
        cls.test_database = f'd_validation_{uuid.uuid4().hex}'

        cls.ch_client_for_setup = HTTPClient(cls.database_host, database=None)
        cls.ch_client_for_setup.query_sync(f"CREATE DATABASE IF NOT EXISTS {cls.test_database} ON CLUSTER tinybird", read_only=False)

        cls.client = HTTPClient(cls.database_host, database=cls.test_database)

    @classmethod
    def tearDownClass(cls):
        cls.ch_client_for_setup.query_sync(f"DROP DATABASE IF EXISTS {cls.test_database} ON CLUSTER tinybird", read_only=False)
        super().tearDownClass()

    def test_describe_query_returns_ok_with_correct_sql(self):
        headers, returned_query = sync_ch_describe_query(self.database_host, self.test_database, "select 1")
        self.assertEqual(returned_query, b"1\tUInt8\t\t\t\t\t\n")
        self.assertEqual(headers['X-Http-Reason'], 'OK')

    def test_describe_different_expressions_with_same_alias_error(self):
        sql = '''
            SELECT
                property_id,
                countMerge(bookings_visits) AS total_bookings
            FROM table_2
            WHERE ((visit_date >= parseDateTimeBestEffort('2021-05-01')) AND (visit_date <= parseDateTimeBestEffort('2021-05-31 23:59:59'))) AND (property_id IN
            (
                    SELECT property_id
                FROM
                (
                        SELECT *
                    FROM table_1
                    WHERE (parseDateTimeBestEffort('2021-05-01') >= min_visit_date) AND (max_visit_date >= (parseDateTimeBestEffort('2021-05-31') - 2)) AND (compset_property_id IN (1000060))
                ) AS t_057a8d989fc0465a92e3668db0e75785
            ))
            GROUP BY property_id
        '''

        table_name = 'table_1'
        engine = f"ReplicatedMergeTree('/clickhouse/tables/{{layer}}-{{shard}}/{self.test_database}.{table_name}','{{replica}}')"
        self.client.query_sync(f"""
            CREATE TABLE {table_name} ON CLUSTER tinybird (key String, property_id Int64, compset_property_id Int64, min_visit_date Date, max_visit_date Date) ENGINE = {engine} Order by compset_property_id
        """, read_only=False)

        engine_2 = f"ReplicatedMergeTree('/clickhouse/tables/{{layer}}-{{shard}}/{self.test_database}.table_2','{{replica}}')"
        self.client.query_sync(f"""
            CREATE TABLE table_2 ON CLUSTER tinybird (visit_date Date, property_id Int64, `bookings_visits` AggregateFunction(count, String)) ENGINE = {engine_2} Partition By toYYYYMM(visit_date) Order by (visit_date, property_id)
        """, read_only=False)

        headers, returned_query = sync_ch_describe_query(self.database_host, self.test_database, sql)
        self.assertEqual(returned_query, b"property_id\tInt64\t\t\t\t\t\ntotal_bookings\tUInt64\t\t\t\t\t\n")
        self.assertEqual(headers['X-Http-Reason'], 'OK')

    def test_describe_query_fails_with_incorrect_sql(self):
        with self.assertRaises(CHException) as context:
            sync_ch_describe_query(self.database_host, self.test_database, "select 1 from x where")

        self.assertEqual(CHErrors.SYNTAX_ERROR, context.exception.code)

    def test_describe_query_fails_with_correct_sql_but_column_not_found(self):
        table_name = "example_table"
        engine = f"ReplicatedMergeTree('/clickhouse/tables/{{layer}}-{{shard}}/{self.test_database}.{table_name}','{{replica}}')"
        self.client.query_sync(f"""
            CREATE TABLE {table_name} ON CLUSTER tinybird (column_a String, column_b String) ENGINE = {engine} Order by tuple()
        """, read_only=False)

        with self.assertRaises(CHException) as context:
            sync_ch_describe_query(
                self.database_host, self.test_database, "SELECT column_a, column_b, column_c FROM example_table")

        self.assertEqual(CHErrors.UNKNOWN_IDENTIFIER, context.exception.code)
        self.assertRegex(context.exception.args[0],
                         r"\[Error\] Missing columns: 'column_c' while processing query: 'SELECT "
                         "column_a, column_b, column_c FROM example_table', required columns: "
                         "'column_a' 'column_b' 'column_c'.*",
                         )

    def test_too_many_parts_error_is_correctly_parsed(self):
        table_name = "test_too_many_parts_error_is_correctly_parsed"
        engine = f"ReplicatedMergeTree('/clickhouse/tables/{{layer}}-{{shard}}/{self.test_database}.{table_name}','{{replica}}')"
        self.client.query_sync(f"""
            CREATE TABLE {table_name} ON CLUSTER tinybird (d Date, n Int32) ENGINE = {engine} PARTITION BY n ORDER BY tuple()
        """, read_only=False)

        with self.assertRaises(CHException) as context:
            self.client.query_sync(f"""
                INSERT INTO {table_name} SELECT toDateTime('2021-01-01 00:00:00', 'UTC'), number as n FROM numbers(101)
            """, read_only=False)

        self.assertEqual(CHErrors.TOO_MANY_PARTS, context.exception.code)
        self.assertRegex(context.exception.args[0], r"\[Error\] Please make sure the ENGINE_PARTITION_KEY setting is correct. Large number of partitions is a common misconception. Partitioning is not intended to speed up SELECT queries \(the ENGINE_SORTING_KEY is sufficient to make range queries fast\), partitions are intended for data manipulation")

    def test_nested_aggregation_function(self):
        with self.assertRaises(CHException) as context:
            self.client.query_sync("""
                SELECT avg(number) AS number, max(number) FROM numbers(10)
            """)

        self.assertEqual(CHErrors.ILLEGAL_AGGREGATION, context.exception.code)
        self.assertEqual(context.exception.args[0], "[Error] You cannot use the aggregate function 'avg(number)' or its alias inside another aggregate function. Contact us at support@tinybird.co for help or read this SQL tip:  https://www.tinybird.co/docs/concepts/data-sources.html#partitioning")

    def test_nested_aggregation_function_with_alias(self):
        with self.assertRaises(CHException) as context:
            self.client.query_sync("""
                SELECT avg(max(number)) FROM numbers(10)
            """)

        self.assertEqual(CHErrors.ILLEGAL_AGGREGATION, context.exception.code)
        self.assertEqual(context.exception.args[0], "[Error] You cannot use the aggregate function 'max(number)' or its alias inside another aggregate function. Contact us at support@tinybird.co for help or read this SQL tip:  https://www.tinybird.co/docs/concepts/data-sources.html#partitioning")

    def test_get_columns_from_query(self):
        sync_ch_get_columns_from_query = async_to_sync(ch_get_columns_from_query)

        res = sync_ch_get_columns_from_query(self.database_host, self.test_database, "select 1 as example")

        self.assertEqual(res, [{
            'name': 'example',
            'normalized_name': 'example',
            'codec': None,
            'type': 'UInt8',
            'nullable': False,
            'auto': False,
            'default_value': None
        }])

    async def test_get_columns_from_complex_query(self):
        table_name = f"big_table_{uuid.uuid4().hex}"
        engine = f"ReplicatedMergeTree('/clickhouse/tables/{{layer}}-{{shard}}/{self.test_database}.{table_name}','{{replica}}')"
        self.client.query_sync(f"""
            CREATE TABLE {table_name} ON CLUSTER tinybird
            ENGINE = {engine}
            ORDER BY number
            AS SELECT * FROM numbers_mt(10000000)
        """, read_only=False)

        start = time.monotonic()
        res = await ch_get_columns_from_query(
            self.database_host, self.test_database, f"""
            SELECT a.number AS first_col, b.number AS sec_col
            FROM {table_name} AS a CROSS JOIN (
                SELECT * from {table_name} PREWHERE number IN (
                    SELECT DISTINCT number FROM {table_name}
                    )
                ) AS b
            """)
        end = time.monotonic()

        self.assertLess(end - start, 0.5, "The operation needs to be fast")

        self.assertEqual(res, [
            {
                'auto': False,
                'codec': None,
                'default_value': None,
                'name': 'first_col',
                'normalized_name': 'first_col',
                'nullable': False,
                'type': 'UInt64'
            },
            {
                'auto': False,
                'codec': None,
                'default_value': None,
                'name': 'sec_col',
                'normalized_name': 'sec_col',
                'nullable': False,
                'type': 'UInt64'
            }
        ])


class TestUnicode(unittest.TestCase):

    def test_case_with_escaped_emojis_returns_ok(self):
        database_host = User.default_database_server
        ch_client = HTTPClient(database_host, database=None)
        headrs, body = ch_client.query_sync("select extractAll(JSONExtractString('{}', 'body'), '[\\\\x{1F600}-\\\\x{1F64F}|\\\\x{1F300}-\\\\x{1F5FF}|\\\\x{1F680}-\\\\x{1F6FF}|\\\\x{1F1E0}-\\\\x{1F1FF}|\\\\x{02702}-\\\\x{027B0}]') emojis FORMAT JSON", read_only=False)
        self.assertEqual([{"emojis": []}], json.loads(body)['data'])


class TestGlobalTimeout(unittest.IsolatedAsyncioTestCase):

    def tearDown(self) -> None:
        global_patch_for_requests_timeout(timeout=(60, 60))

    def test_global_read_timeout_is_applied(self):
        global_patch_for_requests_timeout(timeout=(0.05, 0.05))
        database_host = User.default_database_server
        ch_client = HTTPClient(database_host, database=None)
        with self.assertRaises(requests.exceptions.ReadTimeout):
            ch_client.query_sync("select sleepEachRow(1)", read_only=False)

    def test_global_read_timeout_is_applied_01(self):
        global_patch_for_requests_timeout(timeout=(0.05, 3))
        database_host = User.default_database_server
        ch_client = HTTPClient(database_host, database=None)
        headrs, body = ch_client.query_sync("select sleepEachRow(0.05) as a FORMAT JSON")
        self.assertEqual([{'a': 0}], json.loads(body)['data'])

    def test_global_read_timeout_can_be_overriden(self):
        global_patch_for_requests_timeout(timeout=(0.01, 0.01))
        database_host = User.default_database_server
        ch_client = HTTPClient(database_host, database=None)
        headrs, body = ch_client.query_sync("select sleepEachRow(0.05) as a FORMAT JSON", timeout=10)
        self.assertEqual([{'a': 0}], json.loads(body)['data'])

    async def test_global_read_timeout_is_reduced_by_query_max_execution_time_async(self):
        global_patch_for_requests_timeout(timeout=(10, 10))
        database_host = User.default_database_server
        ch_client = HTTPClient(database_host, database=None)

        query_id = str(uuid.uuid4())
        with self.assertRaises(CHException):
            start = time.time()
            _, _ = await ch_client.query("select sleepEachRow(1) a, sleepEachRow(0.001) as b from system.numbers LIMIT 3",
                                         query_id=query_id, max_execution_time=1, read_only=True)
            end = time.time()
            self.assertLess(end - start, 2)


class TestCHTableQuerySubprocess(unittest.TestCase):

    def test_subprocess_timeout(self):
        columns = [
            {
                'name': 'c0',
                'normalized_name': 'c0',
                'type': 'String',
                'nullable': False,
                'auto': False
            },
            {
                'name': 'c1',
                'normalized_name': 'c1',
                'type': 'Int32',
                'nullable': False,
                'auto': False
            }
        ]
        chunk = """a,1\nb,2\nc,3""".encode()
        fast_query = 'select 0 as s, c0, c1 from table'
        slow_query = 'select sleepEachRow(1) as s, c0, c1 from table'  # simulates stuck subprocess
        t = CHTable(columns)

        output = t.query(chunk, fast_query, timeout=1)
        self.assertEqual(len(output['data']), 3)

        with self.assertRaisesRegex(Exception, r"CH return code: -9"):
            t.query(chunk, slow_query, timeout=0.1)


class TestExtractFromCSVExtract(unittest.TestCase):
    def test_custom_escapechar_easy(self):
        data = """123,"this is \\"just\\" one column, 3 in total",1234\n"""
        info = CSVInfo.extract_from_csv_extract(data, dialect_overrides={'escapechar': '\\', 'delimiter': ',', 'newline': None})
        self.assertEqual(len(info.columns), 3)

    def test_custom_escapechar(self):
        data = """1411820617817640960,0,0,0,0,2021-07-04 22:54:00,"{\\"authorId\\":\\"1475157055\\",\\"handle\\":\\"JustARedFlower\\",\\"userName\\":\\"everyone's mommy\\",\\"followers\\":540,\\"friends\\":774}","",RT @dirtyfourloko: It’s the 4th of July https://t.co/zlCgQBVZOI,"[{\\"type\\":\\"photo\\",\\"expanded_url\\":\\"https://twitter.com/dirtyfourloko/status/1411758352590323712/photo/1\\"}]",[],dirtyfourloko"""
        info = CSVInfo.extract_from_csv_extract(data, dialect_overrides={'escapechar': '\\'})
        self.assertEqual(len(info.columns), 12)


class TestTableDependentViews(unittest.TestCase):

    database_host = User.default_database_server

    test_database_1 = f'test_table_dependent_view_1_{uuid.uuid4().hex}'
    test_database_2 = f'test_table_dependent_view_2_{uuid.uuid4().hex}'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        ch_client_for_setup = HTTPClient(cls.database_host, database=None)
        ch_client_for_setup.query_sync(f"CREATE DATABASE {cls.test_database_1} ON CLUSTER tinybird", read_only=False)
        ch_client_for_setup.query_sync(f"CREATE DATABASE {cls.test_database_2} ON CLUSTER tinybird", read_only=False)
        """
        db test_table_dependent_view_1:
        - ds1
        - mv1: ds1 → ds2
        - ds2
        - table_without_deps

        db test_table_dependent_view_2:
        - mv2: testdb1.ds1 → ds3
        - ds3
        """

        engine_1 = "ReplicatedMergeTree('/clickhouse/tables/{layer}-{shard}/" + f"{cls.test_database_1}.ds1" + "','{replica}')"
        engine_2 = "ReplicatedMergeTree('/clickhouse/tables/{layer}-{shard}/" + f"{cls.test_database_1}.table_without_deps" + "','{replica}')"
        engine_summing_1 = "ReplicatedSummingMergeTree('/clickhouse/tables/{layer}-{shard}/" + f"{cls.test_database_1}.ds2" + "','{replica}')"
        engine_summing_2 = "ReplicatedSummingMergeTree('/clickhouse/tables/{layer}-{shard}/" + f"{cls.test_database_2}.ds3" + "','{replica}')"
        ch_client_for_setup.query_sync(f"CREATE TABLE {cls.test_database_1}.ds1 ON CLUSTER tinybird (value Float32) ENGINE={engine_1} ORDER BY tuple()", read_only=False)
        ch_client_for_setup.query_sync(f"CREATE TABLE {cls.test_database_1}.ds2 ON CLUSTER tinybird (count UInt64) ENGINE = {engine_summing_1} PARTITION BY tuple() ORDER BY tuple()", read_only=False)
        ch_client_for_setup.query_sync(f"CREATE MATERIALIZED VIEW {cls.test_database_1}.mv1 ON CLUSTER tinybird TO {cls.test_database_1}.ds2 AS SELECT count(*) as count FROM {cls.test_database_1}.ds1", read_only=False)
        ch_client_for_setup.query_sync(f"CREATE TABLE {cls.test_database_1}.table_without_deps ON CLUSTER tinybird (value Float32) ENGINE={engine_2} ORDER BY tuple();", read_only=False)

        ch_client_for_setup.query_sync(f"CREATE TABLE {cls.test_database_2}.ds3 ON CLUSTER tinybird (count UInt64) ENGINE = {engine_summing_2} PARTITION BY tuple() ORDER BY tuple();", read_only=False)
        ch_client_for_setup.query_sync(f"CREATE MATERIALIZED VIEW {cls.test_database_2}.mv2 ON CLUSTER tinybird TO {cls.test_database_2}.ds3 AS SELECT count(*) as count FROM {cls.test_database_1}.ds1", read_only=False)

    @classmethod
    def tearDownClass(cls):
        ch_client_for_setup = HTTPClient(cls.database_host, database=None)
        ch_client_for_setup.query_sync(f"DROP DATABASE IF EXISTS {cls.test_database_2} ON CLUSTER tinybird", read_only=False)
        ch_client_for_setup.query_sync(f"DROP DATABASE IF EXISTS {cls.test_database_1} ON CLUSTER tinybird", read_only=False)
        super().tearDownClass()

    def test_dependent_materialized_views_returned_even_when_they_are_in_different_databases(self):
        res = ch_table_dependent_views_sync(self.database_host, self.test_database_1, 'ds1')
        self.assertEqual(2, len(res))
        self.assertIn(CHTableLocation(self.test_database_1, 'mv1'), res)
        self.assertIn(CHTableLocation(self.test_database_2, 'mv2'), res)

    def test_table_without_dependent_views_return_an_empty_result(self):
        res = ch_table_dependent_views_sync(self.database_host, self.test_database_1, 'table_without_deps')
        self.assertEqual([], res)


class TestXClickHouseSummaryHeader(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        super().setUp()
        self.database_host = User.default_database_server
        rand_id = uuid.uuid4().hex
        self.test_database = f'x_ch_summary_{rand_id}'
        self.ch_client_for_setup = HTTPClient(self.database_host, database=None)
        self.ch_client_for_setup.query_sync(f"CREATE DATABASE IF NOT EXISTS {self.test_database} ON CLUSTER tinybird", read_only=False)

        self.client = HTTPClient(self.database_host, database=self.test_database)

    def tearDown(self):
        self.ch_client_for_setup.query_sync(f"DROP DATABASE IF EXISTS {self.test_database} ON CLUSTER tinybird", read_only=False)
        super().tearDown()

    def test_x_clickhouse_summary_header_insert(self):
        table_name = 'summary_table'
        self.client.query_sync(f"CREATE TABLE {table_name} ON CLUSTER tinybird (a String) Engine=Null()", read_only=False)
        headers, _ = self.client.insert_chunk(f'INSERT INTO {table_name} FORMAT CSV', 'value')
        obj = json.loads(headers['X-ClickHouse-Summary'])

        expected_read_rows = '1'
        expected_read_bytes = '14'

        self.assertEqual(obj['read_rows'], expected_read_rows, obj)
        self.assertEqual(obj['read_bytes'], expected_read_bytes, obj)
        self.assertEqual(obj['written_rows'], '1', obj)
        self.assertEqual(obj['written_bytes'], '14', obj)
        self.assertEqual(obj['total_rows_to_read'], '0', obj)
        self.assertTrue(obj['result_rows'] == '1', obj)
        self.assertTrue(obj['result_bytes'] == '14', obj)

    def test_x_clickhouse_summary_header_insert_with_mv(self):
        table_name = "floats"
        engine = f"ReplicatedMergeTree('/clickhouse/tables/{{layer}}-{{shard}}/{self.test_database}.{table_name}.test_x_clickhouse_summary_header_insert_with_mv','{{replica}}')"
        self.client.query_sync(f"CREATE TABLE IF NOT EXISTS {table_name} ON CLUSTER tinybird (v Float64) Engine={engine} order by tuple()", read_only=False)

        headers, _ = self.client.insert_chunk('INSERT INTO floats FORMAT CSV', csv_from_python_object([[1.0]]))

        obj = json.loads(headers['X-ClickHouse-Summary'])

        self.assertEqual(obj['read_rows'], '1', obj)  # 0 in old CH releases, 1 in 22.6+
        self.assertEqual(obj['read_bytes'], '8', obj)  # 0 in old CH releases, 8 in 22.6+
        self.assertEqual(obj['written_rows'], '1', obj)
        self.assertEqual(obj['written_bytes'], '8', obj)
        self.assertEqual(obj['total_rows_to_read'], '0', obj)
        self.assertEqual(obj['result_rows'], '1', obj)  # Added in 22.8+
        self.assertEqual(obj['result_bytes'], '8', obj)  # Added in 22.8+

        table_name_target = "target"
        engine_target = f"ReplicatedMergeTree('/clickhouse/tables/{{layer}}-{{shard}}/{self.test_database}.{table_name_target}','{{replica}}')"
        table_name_target2 = "target2"
        engine_target2 = f"ReplicatedMergeTree('/clickhouse/tables/{{layer}}-{{shard}}/{self.test_database}.{table_name_target2}','{{replica}}')"
        self.client.query_sync(f"CREATE TABLE {table_name_target} ON CLUSTER tinybird (v Float64) Engine={engine_target} order by tuple()", read_only=False)
        self.client.query_sync(f"CREATE TABLE {table_name_target2} ON CLUSTER tinybird (v Float64) Engine={engine_target2} order by tuple()", read_only=False)
        self.client.query_sync(f"CREATE MATERIALIZED VIEW {self.test_database}.floats_to_target ON CLUSTER tinybird TO {self.test_database}.target AS SELECT * FROM {self.test_database}.{table_name}",
                               read_only=False)
        self.client.query_sync(f"CREATE MATERIALIZED VIEW {self.test_database}.floats_to_target2 ON CLUSTER tinybird TO {self.test_database}.target2 AS SELECT * FROM {self.test_database}.{table_name}",
                               read_only=False)

        # Replicated deduplication prevent us from ingesting twice the same value here. Using a different float is key here.
        # See https://clickhouse.com/docs/en/operations/settings/merge-tree-settings/#replicated-deduplication-window
        headers, _ = self.client.insert_chunk('INSERT INTO floats FORMAT CSV', csv_from_python_object([[2.0]]))

        obj = json.loads(headers['X-ClickHouse-Summary'])

        # [rows, bytes]
        post_22_6 = ['1', '8']  # MV not included
        from_22_9 = ['3', '24']  # Landing included
        self.assertIn(obj['read_rows'], [post_22_6[0], from_22_9[0]], obj)
        self.assertIn(obj['read_bytes'], [post_22_6[1], from_22_9[1]], obj)
        self.assertEqual(obj['written_rows'], '3', obj)
        self.assertEqual(obj['written_bytes'], '24', obj)
        self.assertEqual(obj['total_rows_to_read'], '0', obj)
        self.assertEqual(obj['result_rows'], '3', obj)  # Added in 22.8+
        self.assertEqual(obj['result_bytes'], '24', obj)  # Added in 22.8+

    async def test_x_clickhouse_summary_select(self):
        table_name = "floats"
        engine = f"ReplicatedMergeTree('/clickhouse/tables/{{layer}}-{{shard}}/{self.test_database}.{table_name}.test_x_clickhouse_summary_select','{{replica}}')"
        self.client.query_sync(f"CREATE TABLE {table_name} ON CLUSTER tinybird (v Float64) Engine={engine} order by tuple()", read_only=False)
        headers, _ = self.client.insert_chunk('INSERT INTO floats FORMAT CSV', csv_from_python_object([[1.0]]))

        headers, _ = await self.client.query('SELECT * FROM floats')
        obj = json.loads(headers['X-ClickHouse-Summary'])

        self.assertEqual(obj['read_rows'], '1', obj)
        self.assertEqual(obj['read_bytes'], '8', obj)
        self.assertEqual(obj['written_rows'], '0', obj)
        self.assertEqual(obj['written_bytes'], '0', obj)
        self.assertEqual(obj['total_rows_to_read'], '1', obj)
        self.assertTrue('result_rows' not in obj or obj['result_rows'] == '1', obj)  # Added in 22.8+
        self.assertTrue('result_bytes' not in obj or  # noqa: W504
                        # Added in 22.8
                        # 22.10 added more padding to internal structures which means more memory usage
                        # https://github.com/ClickHouse/ClickHouse/pull/42564
                        # Minimum padding before: 64. 22.10+: 256
                        obj['result_bytes'] in ['64', '256'], obj)


class TestOnCluster(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.database_host = User.default_database_server
        cls.test_database = f'd_oncluster_{uuid.uuid4().hex}'

        ch_client_for_setup = HTTPClient(cls.database_host, database=None)
        ch_client_for_setup.query_sync(f"CREATE DATABASE IF NOT EXISTS {cls.test_database} ON CLUSTER tinybird", read_only=False)

        cls.client = HTTPClient(cls.database_host, database=cls.test_database)

    @classmethod
    def tearDownClass(cls):
        ch_client_for_setup = HTTPClient(cls.database_host, database=None)
        ch_client_for_setup.query_sync(f"DROP DATABASE IF EXISTS {cls.test_database} ON CLUSTER tinybird", read_only=False)
        super().tearDownClass()

    async def test_get_query_log_on_cluster(self):
        with patch.object(HTTPClient, 'query', autospec=True) as mock_query_log:
            await _get_query_log(self.database_host, self.test_database, 'query_id', cluster='tinybird')
            query = f"\n        SELECT\n            type,\n            event_time,\n            exception\n        FROM clusterAllReplicas('tinybird', system.query_log)\n        WHERE\n            event_time > now() - INTERVAL 2 DAY\n            AND current_database = '{self.test_database}'\n            AND query_id = 'query_id'\n        ORDER BY\n            event_time DESC\n        FORMAT JSON\n    "
            mock_query_log.assert_called_once_with(ANY, query, max_execution_time=2, skip_unavailable_shards=1)

    async def test_get_query_log(self):
        with patch.object(HTTPClient, 'query', autospec=True) as mock_query_log:
            await _get_query_log(self.database_host, self.test_database, 'query_id')
            query = f"\n        SELECT\n            type,\n            event_time,\n            exception\n        FROM system.query_log\n        WHERE\n            event_time > now() - INTERVAL 2 DAY\n            AND current_database = '{self.test_database}'\n            AND query_id = 'query_id'\n        ORDER BY\n            event_time DESC\n        FORMAT JSON\n    "
            mock_query_log.assert_called_once_with(ANY, query, max_execution_time=2, skip_unavailable_shards=1)

    async def test_ch_flush_logs_on_all_replicas(self):
        clusters = await ch_get_cluster_instances(self.database_host, self.test_database, 'tinybird')

        with patch('tinybird.ch.ch_get_cluster_instances', return_value=clusters):
            with patch.object(HTTPClient, 'query', autospec=True) as mock_query_log:
                await ch_flush_logs_on_all_replicas(self.database_host, 'tinybird', user_agent='test')
                self.assertEqual(mock_query_log.call_count, 2)
                self.assertEqual(mock_query_log.call_args_list[0][0][1], "SYSTEM FLUSH LOGS")
                self.assertEqual(mock_query_log.call_args_list[0][1], {'read_only': False, 'user_agent': 'test', 'max_execution_time': 6})

    def test_ch_flush_logs_on_all_replicas_sync(self):
        clusters = async_to_sync(ch_get_cluster_instances)(self.database_host, self.test_database, 'tinybird')

        with patch('tinybird.ch.ch_get_cluster_instances', return_value=clusters):
            with patch.object(HTTPClient, 'query', autospec=True) as mock_query_log:
                ch_flush_logs_on_all_replicas_sync(self.database_host, 'tinybird', user_agent='test')
                self.assertEqual(mock_query_log.call_count, 2)
                self.assertEqual(mock_query_log.call_args_list[0][0][1], "SYSTEM FLUSH LOGS")
                self.assertEqual(mock_query_log.call_args_list[0][1], {'read_only': False, 'user_agent': 'test', 'max_execution_time': 6})


class TestTruncateTable(unittest.IsolatedAsyncioTestCase):
    database_server = User.default_database_server
    rand_id = uuid.uuid4().hex
    database = f'TestTruncateTable_{rand_id}'
    table = f'table_name_{rand_id}'
    new_table = f'new_table_name_{rand_id}'
    cluster = User.default_cluster

    @classmethod
    def setUpClass(cls):
        engine = f"ReplicatedMergeTree('/clickhouse/tables/{{layer}}-{{shard}}/{cls.database}.{cls.table}','{{replica}}')"
        cls.ch_client_for_setup = HTTPClient(cls.database_server, database=None)
        cls.ch_client_for_setup.query_sync(f"CREATE DATABASE {cls.database} ON CLUSTER {cls.cluster}", read_only=False)
        # We create a special table with has 2 settings things
        # A storage_policy which we could have introduced via feature flag
        # A setting we might have added manually to CH
        cls.ch_client_for_setup.query_sync(f"""
        CREATE TABLE {cls.database}.{cls.table} ON CLUSTER {cls.cluster}
        (
            VisitDate Date,
            Hour UInt8
        )
        ENGINE = {engine}
        PARTITION BY toYYYYMM(VisitDate)
        ORDER BY Hour
        SETTINGS storage_policy = '{OTHER_STORAGE_POLICY}', max_parts_in_total=50000
        """, read_only=False)

    @classmethod
    def tearDownClass(cls):
        cls.ch_client_for_setup.query_sync(f"DROP DATABASE IF EXISTS {cls.database} ON CLUSTER {cls.cluster}", read_only=False)
        super().tearDownClass()

    async def test_ch_create_exact_empty_copy(self):
        await ch_create_exact_empty_copy(self.database_server, self.database,
                                         self.table, self.cluster,
                                         self.new_table)

        table_details = await ch_table_details_async(self.table, self.database_server, self.database)
        new_table_details = await ch_table_details_async(self.new_table, self.database_server, self.database)
        table_meta = table_details.to_json(exclude=['engine_full'])
        new_table_meta = new_table_details.to_json(exclude=['engine_full'])
        self.assertEquals(table_meta, new_table_meta)
        self.assertTrue(table_details.is_replicated())
        self.assertTrue(new_table_details.is_replicated())

        # Make sure both settings survived the copy
        table_details_full = await ch_table_details_async(self.table, self.database_server, self.database, clean_settings=False)
        new_table_details_full = await ch_table_details_async(self.new_table, self.database_server, self.database, clean_settings=False)
        table_meta_full = table_details_full.to_json(exclude=['engine_full'])
        new_table_meta_full = new_table_details_full.to_json(exclude=['engine_full'])
        self.assertEquals(table_meta_full, new_table_meta_full)
        self.assertIn('storage_policy', new_table_details_full.engine_full)
        self.assertIn('storage_policy', new_table_details_full.settings)
        self.assertIn('max_parts_in_total', new_table_details_full.engine_full)
        self.assertIn('max_parts_in_total', new_table_details_full.settings)

    async def test_ch_truncate_table(self):
        table_to_truncate = f"table_to_truncate_{self.rand_id}"
        engine = f"ReplicatedMergeTree('/clickhouse/tables/{{layer}}-{{shard}}/{self.database}.{table_to_truncate}', '{{replica}}')"
        ch_client = HTTPClient(self.database_server, database=None)
        ch_client.query_sync(f"""
        CREATE TABLE {self.database}.{table_to_truncate} ON CLUSTER {self.cluster}
        (
            VisitDate Date,
            Hour UInt8
        )
        ENGINE = {engine}
        PARTITION BY toYYYYMM(VisitDate)
        ORDER BY Hour;
        """, read_only=False)
        ch_client.query_sync(f"""
        INSERT INTO {self.database}.{table_to_truncate} (*)
        VALUES ('2022-08-24',7)""", read_only=False)
        previous_response = ch_client.query_sync(f"""
        SELECT * from {self.database}.{table_to_truncate}""", read_only=False)[-1]
        self.assertTrue(previous_response.decode('utf-8'))
        await ch_truncate_table(self.database_server, self.database,
                                table_to_truncate, self.cluster)
        truncated_response = ch_client.query_sync(f"""
        SELECT * from {self.database}.{table_to_truncate}""", read_only=False)[-1]
        self.assertFalse(truncated_response.decode('utf-8'))

    async def test_ch_truncate_table_with_fallback_happy_path(self):
        with unittest.mock.patch('tinybird.ch.ch_truncate_table') as mock_ch_truncate_table:
            await ch_truncate_table_with_fallback(self.database_server, self.database, self.table, self.cluster)
            mock_ch_truncate_table.assert_called_once()

    async def test_ch_truncate_table_with_fallback_generic_error(self):
        ch_exception = CHException('Code: 32, e.displayText() = DB::Exception: Attempt to read after eof: Cannot parse Int16 from String, because value is too short (version 19.13.1.1)')
        with unittest.mock.patch('tinybird.ch.ch_truncate_table', side_effect=ch_exception):
            with self.assertRaises(CHException):
                await ch_truncate_table_with_fallback(self.database_server, self.database, self.table, self.cluster)

    async def test_ch_truncate_table_with_fallback_table_size_exceeds_max_drop_size(self):
        ch_exception = CHException('Code: 359, e.displayText = DB::Exception: Table or Partition in table_name was not dropped.')
        with unittest.mock.patch('tinybird.ch.ch_truncate_table', side_effect=ch_exception):
            with unittest.mock.patch('tinybird.ch.ch_create_exact_empty_copy') as mock_ch_create_exact_empty_copy:
                with unittest.mock.patch('tinybird.ch.ch_swap_tables') as mock_ch_swap_tables:
                    await ch_truncate_table_with_fallback(self.database_server, self.database, self.table, self.cluster)
                    mock_ch_create_exact_empty_copy.assert_called_once()
                    mock_ch_swap_tables.assert_called_once()


async def wait_for_query_start(client, query_id):
    i = 0
    while i < 10:
        query = f"""SELECT count() c from clusterAllReplicas('tinybird', 'system.processes') where query_id='{query_id}' format JSON"""
        _, body = await client.query(query)
        data = json.loads(body)['data']
        if data[0]['c'] >= 1:
            break
        try:
            await asyncio.sleep(0.05)
        except RuntimeError:
            time.sleep(0.05)
        i += 1
    if i == 10:
        raise RuntimeError('query did not start')


class TestQuery(unittest.IsolatedAsyncioTestCase):

    async def test_response_is_compress(self):
        database_host = User.default_database_server
        client = HTTPClient(database_host, database=None)

        headers, body = await client.query("SELECT number FROM numbers(10) FORMAT JSON", compress=True)
        body = zlib.decompress(body, wbits=16 + 15)

        rows = json.loads(body).get('data', [])
        self.assertEqual(len(rows), 10, body)
        self.assertEqual(headers['Content-Encoding'], 'gzip', headers)


class TestExplainEstimate(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        super().setUp()
        rand_id = uuid.uuid4().hex
        self.database_host = User.default_database_server
        self.test_database = f'x_explain_estimate_{rand_id}'
        self.ch_client_for_setup = HTTPClient(self.database_host, database=None)
        self.ch_client_for_setup.query_sync(f"CREATE DATABASE IF NOT EXISTS {self.test_database} ON CLUSTER tinybird", read_only=False)

        self.client = HTTPClient(self.database_host, database=self.test_database)

    def tearDown(self):
        self.ch_client_for_setup.query_sync(f"DROP DATABASE IF EXISTS {self.test_database} ON CLUSTER tinybird", read_only=False)
        super().tearDown()

    async def create_table_and_insert_chunk(self, table_name, table_definition, chunk):
        await self.client.query(table_definition, read_only=False)
        self.client.query_sync(f"INSERT INTO {self.test_database}.{table_name} VALUES ({chunk})", read_only=False)

    async def test_explain_estimate_returns_sum_of_rows(self):
        first_table_name = 't_test_explain_estimate_returns_sum_of_rows_1'
        second_table_name = 't_test_explain_estimate_returns_sum_of_rows_2'

        await self.create_table_and_insert_chunk(
            first_table_name,
            f"""CREATE TABLE {self.test_database}.{first_table_name} ON CLUSTER tinybird (example String)
                Engine=ReplicatedMergeTree('/clickhouse/tables/{{layer}}-{{shard}}/{self.test_database}.{first_table_name}','{{replica}}') PARTITION BY example ORDER BY tuple()""",
            "'test_string'"
        )

        await self.create_table_and_insert_chunk(
            second_table_name,
            f"""CREATE TABLE {self.test_database}.{second_table_name} ON CLUSTER tinybird (example String)
                Engine=ReplicatedMergeTree('/clickhouse/tables/{{layer}}-{{shard}}/{self.test_database}.{second_table_name}','{{replica}}') PARTITION BY example ORDER BY tuple()""",
            "'test_string'"
        )

        CHReplication.ch_wait_for_replication_sync(self.database_host, 'tinybird', self.test_database, first_table_name)
        CHReplication.ch_wait_for_replication_sync(self.database_host, 'tinybird', self.test_database, second_table_name)

        estimated_rows = await ch_estimate_query_rows(
            self.database_host,
            self.test_database,
            f'SELECT * FROM {first_table_name} a JOIN {second_table_name} b ON a.example = b.example'
        )

        self.assertEqual(estimated_rows, 2)
