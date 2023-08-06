from tinybird.ch import HTTPClient
from tinybird.pg import PGService
from tinybird.user import Users
from tinybird.token_scope import scopes

from .conftest import CH_HOST, CH_HTTP_PORT
from .views.base_test import BaseTest


def create_test_tables(database_server, database):
    def _get_replicated_engine(database, table_name):
        return f"ReplicatedMergeTree('/clickhouse/tables/{{layer}}-{{shard}}/{database}.{table_name}','{{replica}}')"

    def _get_replicated_aggregating_engine(database, table_name):
        return f"ReplicatedAggregatingMergeTree('/clickhouse/tables/{{layer}}-{{shard}}/{database}.{table_name}','{{replica}}')"

    create_tables = [
        f"""
        CREATE TABLE IF NOT EXISTS {database}.ints ON CLUSTER tinybird (
            c1 Int8, c2 Int16, c3 Int32, c4 Int64,
            c5 UInt8, c6 UInt16, c7 UInt32, c8 UInt64,
            c9 Int128, c10 UInt128,
            c11 Int256, c12 UInt256,
            c13 Float32, c14 Nullable(Float64)
        ) ENGINE = {_get_replicated_engine(database, f'ints')} PARTITION BY c1 ORDER BY (c1);
        """,
        f"""
        CREATE TABLE IF NOT EXISTS {database}.types ON CLUSTER tinybird (
            c1 Date, c2 DateTime, c3 String, c4 FixedString(5), c5 UUID,
            c6 Enum8('one' = 1, 'two' = 2),
            c7 Enum16('one' = 1, 'two' = 2, 'three' = 3),
            c9 Nullable(FixedString(50)),
            c8 LowCardinality(String), c10 Nullable(UInt8)
        ) ENGINE = {_get_replicated_engine(database, f'types')} PARTITION BY c1 ORDER BY (c1);
        """,
        f"""
        CREATE TABLE IF NOT EXISTS {database}.arrays ON CLUSTER tinybird (
            c1 Array(Int),
            c2 Array(String),
            c3 Array(DateTime),
            c4 Array(Tuple(String, Float32))
        ) ENGINE = {_get_replicated_engine(database, f'arrays')} PARTITION BY c1 ORDER BY (c1);
        """,
        f"""
        CREATE TABLE IF NOT EXISTS {database}.tuples ON CLUSTER tinybird (
            c1 Int8,
            c2 Tuple(Int, String, Float32),
            c3 Nested(a Int, b Int),
            c4 Tuple(Float64, Float64)
        ) ENGINE = {_get_replicated_engine(database,f'tuples')} PARTITION BY c1 ORDER BY (c1);
        """,
        f"""
        CREATE TABLE IF NOT EXISTS {database}.dt ON CLUSTER tinybird (
            c1 Int32,
            c2 DateTime('Europe/Moscow'),
            c3 DateTime('Europe/Berlin'),
            c4 DateTime
        ) ENGINE = {_get_replicated_engine(database, f'dt')} PARTITION BY c1 ORDER BY (c1);
        """,
        f"""
        CREATE TABLE IF NOT EXISTS {database}.dt64 ON CLUSTER tinybird (
            c1 Int32,
            c2 DateTime64(6, 'Europe/Moscow'),
            c3 DateTime64(9, 'Europe/Berlin'),
            c4 DateTime64(3),
            c5 DateTime64(6),
            c6 Array(DateTime64(3))
        ) ENGINE = {_get_replicated_engine(database,f'dt64')} PARTITION BY c1 ORDER BY (c1);
        """,
        f"""
        create table if not exists {database}.t1 on cluster tinybird (a int, b int)
            engine = {_get_replicated_engine(database, f't1')}
            order by a
        """,
        f"""
        create table if not exists {database}.t2 on cluster tinybird (a int, b AggregateFunction(sum, Int32))
            engine = {_get_replicated_aggregating_engine(database, f't2')}
            order by a
        """,
        f"""
        create table if not exists {database}.t3 on cluster tinybird (a int, b Array(Int32), c Array(Int32))
            engine = {_get_replicated_engine(database, f't3')}
            order by a
        """,
        f"""
        create table if not exists {database}.t4 on cluster tinybird (a int,
            b AggregateFunction(sum, Int32),
            d SimpleAggregateFunction(sum, Int64))
        engine = {_get_replicated_aggregating_engine(database, f't4')}
        order by a
        """,
        f"""
        create materialized view if not exists {database}.t1_aggr on cluster tinybird
            engine={_get_replicated_aggregating_engine(database, f't1_aggr')}
            order by a populate as select a, sumState(b) as b from {database}.t1 group by a;
        """,
        # """
        # create materialized view t3_aggr
        #     engine=AggregatingMergeTree()
        #     order by a populate as select a, sumMapState(b, c) as b from t3 group by a;
        # """,
        f"""
        CREATE TABLE IF NOT EXISTS {database}.ips ON CLUSTER tinybird (
            c1 IPv4, c2 IPv6
        ) ENGINE = {_get_replicated_engine(database, f'ips')} PARTITION BY c1 ORDER BY (c1);
        """,
        f"""
        CREATE VIEW IF NOT EXISTS {database}.view ON CLUSTER tinybird (
            c1 Int8, c100 Nullable(Nothing)
        ) AS SELECT c1 FROM {database}.ints;
        """
    ]

    client = HTTPClient(database_server, database=database)
    for query in create_tables:
        client.query_sync(query, read_only=False)

    expect_tables = {
        'ints': f"""CREATE FOREIGN TABLE IF NOT EXISTS "ints" ("c1" INT2 NOT NULL, "c2" INT2 NOT NULL, "c3" INT4 NOT NULL, "c4" INT8 NOT NULL, "c5" INT2 NOT NULL, "c6" INT4 NOT NULL, "c7" INT8 NOT NULL, "c8" NUMERIC NOT NULL, "c9" NUMERIC NOT NULL, "c10" NUMERIC NOT NULL, "c11" NUMERIC NOT NULL, "c12" NUMERIC NOT NULL, "c13" REAL NOT NULL, "c14" DOUBLE PRECISION) SERVER "fdw_{database}" OPTIONS(table_name \'ints\', engine \'ReplicatedMergeTree\')""",
        'types': f"""CREATE FOREIGN TABLE IF NOT EXISTS "types" ("c1" DATE NOT NULL, "c2" TIMESTAMP NOT NULL, "c3" TEXT NOT NULL, "c4" VARCHAR(5) NOT NULL, "c5" UUID NOT NULL, "c6" TEXT NOT NULL, "c7" TEXT NOT NULL, "c9" VARCHAR(50) , "c8" TEXT NOT NULL, "c10" INT2) SERVER "fdw_{database}" OPTIONS(table_name 'types', engine 'ReplicatedMergeTree')""",
        'arrays': f"""CREATE FOREIGN TABLE IF NOT EXISTS "arrays" ("c1" INT4[] NOT NULL, "c2" TEXT[] NOT NULL, "c3" TIMESTAMP[] NOT NULL, "c4" TEXT[] NOT NULL) SERVER "fdw_{database}" OPTIONS(table_name \'arrays\', engine \'ReplicatedMergeTree\')""",
        'tuples': f"""CREATE FOREIGN TABLE IF NOT EXISTS "tuples" ("c1" INT2 NOT NULL, "c2" TEXT NOT NULL, "c3.a" INT4[] NOT NULL, "c3.b" INT4[] NOT NULL, "c4" TEXT NOT NULL) SERVER "fdw_{database}" OPTIONS(table_name \'tuples\', engine \'ReplicatedMergeTree\')""",
        'dt': f"""CREATE FOREIGN TABLE IF NOT EXISTS "dt" ("c1" INT4 NOT NULL, "c2" TIMESTAMP NOT NULL, "c3" TIMESTAMP NOT NULL, "c4" TIMESTAMP NOT NULL) SERVER "fdw_{database}" OPTIONS(table_name \'dt\', engine \'ReplicatedMergeTree\')""",
        'dt64': f"""CREATE FOREIGN TABLE IF NOT EXISTS "dt64" ("c1" INT4 NOT NULL, "c2" TIMESTAMP NOT NULL, "c3" TIMESTAMP NOT NULL, "c4" TIMESTAMP NOT NULL, "c5" TIMESTAMP NOT NULL, "c6" TIMESTAMP[] NOT NULL) SERVER "fdw_{database}" OPTIONS(table_name \'dt64\', engine \'ReplicatedMergeTree\')""",
        't1': f"""CREATE FOREIGN TABLE IF NOT EXISTS "t1" ("a" INT4 NOT NULL, "b" INT4 NOT NULL) SERVER "fdw_{database}" OPTIONS(table_name 't1', engine 'ReplicatedMergeTree')""",
        't2': f"""CREATE FOREIGN TABLE IF NOT EXISTS "t2" ("a" INT4 NOT NULL, "b" INT4 OPTIONS(AggregateFunction 'sum') NOT NULL) SERVER "fdw_{database}" OPTIONS(table_name 't2', engine 'ReplicatedAggregatingMergeTree')""",
        't3': f"""CREATE FOREIGN TABLE IF NOT EXISTS "t3" ("a" INT4 NOT NULL, "b" INT4[] NOT NULL, "c" INT4[] NOT NULL) SERVER "fdw_{database}" OPTIONS(table_name 't3', engine 'ReplicatedMergeTree')""",
        't4': f"""CREATE FOREIGN TABLE IF NOT EXISTS "t4" ("a" INT4 NOT NULL, "b" INT4 OPTIONS(AggregateFunction 'sum') NOT NULL, "d" INT8 OPTIONS(AggregateFunction 'sum') NOT NULL) SERVER "fdw_{database}" OPTIONS(table_name 't4', engine 'ReplicatedAggregatingMergeTree')""",
        't1_aggr': f"""CREATE FOREIGN TABLE IF NOT EXISTS "t1_aggr" ("a" INT4 NOT NULL, "b" INT4 OPTIONS(AggregateFunction 'sum') NOT NULL) SERVER "fdw_{database}" OPTIONS(table_name 't1_aggr', engine 'MaterializedView')""",
        # 't3_aggr': """
        #     create materialized view t3_aggr
        #         engine=AggregatingMergeTree()
        #         order by a populate as select a, sumMapState(b, c) as b from t3 group by a;
        #     """,
        'ips': f"""CREATE FOREIGN TABLE IF NOT EXISTS "ips" ("c1" inet NOT NULL, "c2" inet NOT NULL) SERVER "fdw_{database}" OPTIONS(table_name 'ips', engine 'ReplicatedMergeTree')""",
        'view': f"""CREATE FOREIGN TABLE IF NOT EXISTS "view" ("c1" INT2 NOT NULL, "c100" TEXT) SERVER "fdw_{database}" OPTIONS(table_name 'view', engine 'None')""",  # The engine is View. We do not allow Views inside the product. This is only needed for a ITX "hackerismo".
    }

    return expect_tables


class TestPGService(BaseTest):
    def setUp(self):
        super().setUp()
        self.create_test_datasource()
        u = Users.get_by_id(self.WORKSPACE_ID)
        self.u = u
        self.admin_token = Users.get_token_for_scope(u, scopes.ADMIN)
        # drop the database in case it already exists
        self.u['enabled_pg'] = True
        self.u['pg_server'] = '127.0.0.1'
        self.u['pg_foreign_server'] = CH_HOST
        self.u['pg_foreign_server_port'] = CH_HTTP_PORT
        self.pg_service = PGService(self.u)

    def tearDown(self):
        self.u['enabled_pg'] = True
        self.pg_service.drop_database()
        self.u['enabled_pg'] = False
        super().tearDown()

    def test_does_nothing_if_not_enabled_pg(self):
        self.u['enabled_pg'] = True
        self.pg_service.drop_database()
        self.u['enabled_pg'] = False
        self.pg_service.setup_database()

        result = self.pg_service.execute("SELECT oid FROM pg_database WHERE datname = %s;", params=[self.pg_service.get_database_name()])
        self.assertEqual(len(result), 0)

    def test_setup_database(self):
        self.pg_service.setup_database()
        result = self.pg_service.execute("SELECT oid FROM pg_database WHERE datname = %s;", params=[self.pg_service.get_database_name()])
        self.assertEqual(len(result), 1)

    def test_sync_foreign_tables(self):
        self.pg_service.setup_database()
        result = self.pg_service.execute("SELECT oid FROM pg_database WHERE datname = %s;", params=[self.pg_service.get_database_name()])
        self.assertEqual(len(result), 1)

        self.pg_service.sync_foreign_tables()

        sql = "SELECT * FROM pg_views WHERE viewname = 'test_table' AND schemaname = 'public';"
        result = self.pg_service.execute(sql, role='user')
        self.assertEqual(len(result), 1)

        sql = "SELECT count(*) FROM test_table;"
        result = self.pg_service.execute(sql, role='user')
        self.assertEqual(result[0]['count'], 6)

    def test_create_foreign_tables(self):
        self.pg_service.setup_database()
        result = self.pg_service.execute("SELECT oid FROM pg_database WHERE datname = %s;", params=[self.pg_service.get_database_name()])
        self.assertEqual(len(result), 1)

        expect_tables = create_test_tables(self.u['database_server'], self.u['database'])

        for table_name in expect_tables.keys():
            view_name = f'v_{table_name}'

            # pre-checks
            sql = f"SELECT * FROM information_schema.tables WHERE table_type = 'FOREIGN' AND table_name = '{table_name}' AND table_schema = 'public';"
            result = self.pg_service.execute(sql, role='user')
            self.assertEqual(len(result), 0)

            sql = f"SELECT * FROM pg_views WHERE viewname = '{view_name}' AND schemaname = 'public';"
            result = self.pg_service.execute(sql, role='user')
            self.assertEqual(len(result), 0)

            # create
            ft = self.pg_service.create_foreign_table(table_name, view_name)
            expect_sql = ft.replace('\n', ' ').replace('  ', '').strip()
            self.assertEqual(expect_sql, expect_tables[table_name])

            # post-checks
            sql = f"SELECT * FROM information_schema.tables WHERE table_type = 'FOREIGN' AND table_name = '{table_name}' AND table_schema = 'public';"
            result = self.pg_service.execute(sql, role='user')
            self.assertEqual(len(result), 1)

            sql = f"SELECT * FROM pg_views WHERE viewname = '{view_name}' AND schemaname = 'public';"
            result = self.pg_service.execute(sql, role='user')
            self.assertEqual(len(result), 1)

    def test_drop_foreign_table(self):
        self.pg_service.setup_database()
        result = self.pg_service.execute("SELECT oid FROM pg_database WHERE datname = %s;", params=[self.pg_service.get_database_name()])
        self.assertEqual(len(result), 1)

        self.pg_service.sync_foreign_tables()

        self.pg_service.drop_foreign_table(self.u.get_datasources()[0].id)
        sql = "SELECT * FROM pg_views WHERE viewname = 'test_table' AND schemaname = 'public';"
        result = self.pg_service.execute(sql, role='user')
        self.assertEqual(len(result), 0)

    def test_alter_datasource_name(self):
        self.pg_service.setup_database()
        result = self.pg_service.execute("SELECT oid FROM pg_database WHERE datname = %s;", params=[self.pg_service.get_database_name()])
        self.assertEqual(len(result), 1)

        self.pg_service.sync_foreign_tables()

        self.pg_service.alter_datasource_name(self.u.get_datasources()[0].name, 'prapra')
        sql = "SELECT * FROM pg_views WHERE viewname = 'test_table' AND schemaname = 'public';"
        result = self.pg_service.execute(sql, role='user')
        self.assertEqual(len(result), 0)

        sql = "SELECT * FROM pg_views WHERE viewname = 'prapra' AND schemaname = 'public';"
        result = self.pg_service.execute(sql, role='user')
        self.assertEqual(len(result), 1)

        sql = "SELECT count(*) as c FROM prapra;"
        result = self.pg_service.execute(sql, role='user')
        self.assertEqual(result[0]['c'], 6)

    def test_queries_from_postgres_carries_correct_current_database_and_user_agent(self):
        self.pg_service.setup_database()
        result = self.pg_service.execute("SELECT oid FROM pg_database WHERE datname = %s;", params=[self.pg_service.get_database_name()])
        self.assertEqual(len(result), 1)

        self.pg_service.sync_foreign_tables()

        sql = "SELECT count(*) from test_table"
        result = self.pg_service.execute(sql, role='user')
        self.assertEqual(len(result), 1)

        query_log_row_new = self.get_query_logs_by_where(f"query = 'SELECT count(*) FROM {self.u.database}.{self.u.get_datasources()[0].id}'")

        self.assertEqual(query_log_row_new[0]['http_user_agent'], 'postgres')
        self.assertEqual(query_log_row_new[0]['current_database'], self.u.database)
