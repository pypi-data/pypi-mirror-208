import unittest

from chtoolset import query as chquery
from tinybird.sql_toolset import replace_tables


class TestSQLBasic(unittest.TestCase):
    sql = "SELECT * FROM table_a"

    def test_replace(self):
        replaced = replace_tables(self.sql, {
            'table_a': '__t_id_1'
        })
        self.assertEqual(replaced, chquery.format("SELECT * FROM __t_id_1 as table_a"))

    def test_replace_default_database(self):
        replaced = replace_tables(self.sql, {
            'table_a': '__t_id_1'
        }, default_database='d_012345')
        self.assertEqual(replaced, chquery.format("SELECT * FROM d_012345.__t_id_1 as table_a"))

    def test_replace_tuple_default_database(self):
        replaced = replace_tables("SELECT * FROM db_1.table_a", {
            ('db_1', 'table_a'): '__t_id_1'
        }, default_database='d_012345')
        self.assertEqual(replaced, chquery.format("SELECT * FROM d_012345.__t_id_1 as table_a"))


class TestSQLMultipleTables(unittest.TestCase):
    def test_replace_tables(self):
        sql = """
            SELECT
                table_a.col0,
                a.col1,
                b.col0
            FROM table_a as a any inner join (
                SELECT * FROM db_2.table_b
            ) as b USING unified
        """
        replaced = replace_tables(sql, {
            'table_a': '__t_id_1',
            ('db_2', 'table_b'): '__t_id_2'
        })
        self.assertEqual(replaced, chquery.format("""
            SELECT
                __t_id_1.col0,
                a.col1,
                b.col0
            FROM __t_id_1 as a any inner join (
                SELECT * FROM __t_id_2 as table_b
            ) as b USING unified
        """))

    def test_replace_tables_default_database(self):
        sql = """
            SELECT
                db_1.table_a.*,
                table_a.col0,
                a.col1,
                b.col0
            FROM table_a as a any inner join (
                SELECT * FROM db_2.table_b
            ) as b USING unified
        """
        replaced = replace_tables(sql, {
            'table_a': '__t_id_1',
            ('db_1', 'table_a'): '__t_id_1',
            ('db_2', 'table_b'): '__t_id_2'
        }, default_database='db_1')
        self.assertEqual(replaced, chquery.format("""
            SELECT
                db_1.__t_id_1.*,
                __t_id_1.col0,
                a.col1,
                b.col0
            FROM db_1.__t_id_1 as a any inner join (
                SELECT * FROM db_1.__t_id_2 AS table_b
            ) as b USING unified
        """))


class TestSQLComplexQueries(unittest.TestCase):
    def test_replace_with_join_default_database(self):
        sql = """
        select * from (
            select * from (
                select * from listings where city like '_evill_'
            ) as f
            UNION ALL
            select * from (
                select * from checkings as cc any left join (
                    select unifiedid, city, bedrooms from listings where city = 'Seville'
                ) aa using unifiedid
            ) as l_13
        ) limit 100
        """
        replaced = replace_tables(sql, {
            'listings': 'l1',
            'checkings': 'c1'
        }, default_database='d_012345')
        self.assertEqual(replaced, chquery.format("""
        select * from (
            select * from (
                select * from d_012345.l1 as listings where city like '_evill_'
            ) as f
            UNION ALL
            select * from (
                select * from d_012345.c1 as cc any left join (
                    select unifiedid, city, bedrooms from d_012345.l1 as listings where city = 'Seville'
                ) aa using unifiedid
            ) as l_13
        ) limit 100
        """))

    # Worked well in 0.14.dev1 and previous releases, and 0.15.dev1+.
    # Broken in 0.15.dev0: aliases column names didn't work in the second replacement (the first one was ok)
    # Got:          traceback,
    # Expected:     JSONExtract(tags, 'traceback', 'Array(String)') AS traceback,
    def test_replace_with_join_with_inner_aliases(self):
        self.maxDiff = None
        spans_500_errors_sql = """
            SELECT
                start_datetime,
                workspace_name,
                status_code,
                method,
                url,
                error,
                JSONExtract(tags, 'traceback', 'Array(String)') traceback,
                logs,
                tags,
                operation_name
            FROM Internal.spans
            where start_datetime > now() - INTERVAL 1 day
            and status_code >= 500
            and kind = 'server'
            and component = 'tornado'
            ORDER BY start_datetime DESC
        """

        spans_500_error_count = """
            SELECT
                count() as 500_errors_count,
                500_errors_count as k_500_errors_count,
                uniq(cityHash64(error, traceback)) as uniq_errors
            FROM (
                SELECT * FROM untitled_pipe_7234_0
                WHERE start_datetime > now() - INTERVAL 1 day
            ) a
            join (
                SELECT * FROM untitled_pipe_7234_0
                WHERE start_datetime > now() - INTERVAL 1 day
            ) b
            using k_500_errors_count
            WHERE 1
            ORDER BY 500_errors_count DESC
        """

        replacement = {('default', 'untitled_pipe_7234_0'): ('', '(' + spans_500_errors_sql + ')'), ('Internal', 'spans'): ('', 'spans')}
        replaced = replace_tables(spans_500_error_count, replacement, default_database='default')

        self.assertEqual(replaced, chquery.format("""
            SELECT
                count() AS `500_errors_count`,
                `500_errors_count` AS k_500_errors_count,
                uniq(cityHash64(error, traceback)) AS uniq_errors
            FROM
            (
                SELECT *
                FROM
                (
                    SELECT
                        start_datetime,
                        workspace_name,
                        status_code,
                        method,
                        url,
                        error,
                        JSONExtract(tags, 'traceback', 'Array(String)') AS traceback,
                        logs,
                        tags,
                        operation_name
                    FROM default.spans
                    WHERE (start_datetime > (now() - toIntervalDay(1))) AND (status_code >= 500) AND (kind = 'server') AND (component = 'tornado')
                    ORDER BY start_datetime DESC
                ) AS untitled_pipe_7234_0
                WHERE start_datetime > (now() - toIntervalDay(1))
            ) AS a
            INNER JOIN
            (
                SELECT *
                FROM
                (
                    SELECT
                        start_datetime,
                        workspace_name,
                        status_code,
                        method,
                        url,
                        error,
                        JSONExtract(tags, 'traceback', 'Array(String)') AS traceback,
                        logs,
                        tags,
                        operation_name
                    FROM default.spans
                    WHERE (start_datetime > (now() - toIntervalDay(1))) AND (status_code >= 500) AND (kind = 'server') AND (component = 'tornado')
                    ORDER BY start_datetime DESC
                ) AS untitled_pipe_7234_0
                WHERE start_datetime > (now() - toIntervalDay(1))
            ) AS b USING (k_500_errors_count)
            WHERE 1
            ORDER BY `500_errors_count` DESC
        """))


class TestSQLReplaceTables(unittest.TestCase):

    scenarios = [
        ('select * from tt', {'tt': 'table2'}, 'select * from table2 as tt'),
        ('select * from tt', {'tt': '(select a from table2 where a > 1)'}, 'select * from (select a from table2 where a > 1) AS tt'),
        ('select tt.a from tt', {'tt': '(select a from table2 where a > 1)'}, 'select tt.a from (select a from table2 where a > 1) AS tt'),
        ('select tt.* from tt', {'tt': '(select a from table2 where a > 1)'}, 'select tt.* from (select a from table2 where a > 1) AS tt'),
        ('select aa.a from tt AS aa', {'tt': '(select a from table2 where a > 1)'}, 'select aa.a from (select a from table2 where a > 1) AS aa'),
        ('select * from database.tt', {('database', 'tt'): '(select a from table2 where a > 1)'}, 'select * from (select a from table2 where a > 1) AS tt'),
        ('select * from database.`tt`', {('database', 'tt'): '(select a from table2 where a > 1)'}, 'select * from (select a from table2 where a > 1) AS tt'),
        ('select * from `database`.`tt`', {('database', 'tt'): '(select a from table2 where a > 1)'}, 'select * from (select a from table2 where a > 1) AS tt'),
        ('select * from tt inner join ttj using b', {'tt': 'tt2', 'ttj': 'ttj2'}, 'select * from tt2 as tt inner join ttj2 as ttj using b'),
        ('select * from tt inner join tt using b', {'tt': 'tt2'}, 'select * from tt2 as tt inner join tt2 as tt using b'),
        ('select count() c from test_table format JSON', {'test_table': 'pepe'}, 'select count() c from pepe as test_table format JSON'),
        ('select * from tt', {'tt': ('d_012345', 'table2')}, 'select * from d_012345.table2 as tt'),
        (
            'select count() as t, t.record, avg(landing.timestamp) from landing t group by t.record',
            {'landing': ('database', 't_01010101')},
            'select count() as t, t.record, avg(t_01010101.timestamp) from database.t_01010101 t group by t.record'
        ),
    ]

    def test_replace(self):
        for (sql, replacements, expected_query) in self.scenarios:
            with self.subTest(sql=sql):
                self.assertEqual(replace_tables(sql, replacements), chquery.format(expected_query))


class TestSQLReplaceTablesWithDeps(unittest.TestCase):

    scenarios = [
        (
            'select * from test',
            {
                'test': 'testing'
            },
            'select * from testing AS test'
        ),
        (
            'select * from test',
            {
                'test': '(select * from testing)'
            },
            'select * from (select * from testing) as test'
        ),
        (
            'select * from test',
            {
                'test': '(select * from test0)',
                'test0': 'test_id'
            },
            'select * from (select * from test_id as test0) as test'
        ),
        (
            'select * from test',
            {
                'test': '(select * from test0)',
                'test0': 'test_id',
                'test_id': 'test_id_on_disk'
            },
            'select * from (select * from test_id_on_disk as test0) as test'
        ),
        (
            'select * from test',
            {
                'test': '(select * from test0)',
                'test0': 'test_id',
                'test_id': 'test_id_on_disk',
                'test_id_on_disk': '(select * from test_id_on_disk where a > 10)'
            },
            'select * from (select * from (select * from test_id_on_disk where a > 10) as test0) AS test'
        ),
        (
            'select * from test',
            {
                'test': '(select * from test0)',
                'test0': '(select * from test_id inner join wadus using b)',
                'test_id': 'test_id_on_disk',
                'wadus': '(select * from wadus_src where c < 1000)'
            },
            'select * from (select * from (select * from test_id_on_disk as test_id inner join (select * from wadus_src where c < 1000) as wadus using b) as test0) as test'
        ),
        (
            'select * from test',
            {
                'test': '(select * from test0)',
                'test0': '(select * from test_id inner join wadus using b)',
                'test_id': 'test_id_on_disk',
                'wadus': '(select * from wadus_src where c < 1000)',
                'test_id_on_disk': '(select * from test_id_on_disk where a > 10)'
            },
            'select * from (select * from (select * from (select * from test_id_on_disk where a > 10) as test_id inner join (select * from wadus_src where c < 1000) as wadus using b) as test0) as test'
        ),
        (
            'select * from a left join b on a.id = b.id',
            {
                'a': '(select * from test0 where id > 1)',
                'b': '(select * from test1 where id > 1)',
            },
            'select * from (select * from test0 where id > 1) as a left join (select * from test1 where id > 1) as b on a.id = b.id'
        ),
        (
            'select * from a as a_alias left join b  b_alias on a_alias.id = b_alias.id',
            {
                'a': '(select * from test0 where id > 1)',
                'b': '(select * from test1 where id > 1)',
            },
            'select * from (select * from test0 where id > 1) as a_alias left join (select * from test1 where id > 1) as b_alias on a_alias.id = b_alias.id'
        ),
        # https://gitlab.com/tinybird/analytics/-/issues/1964
        (
            'SELECT count() FROM test_pipe_1',
            {
                'test_pipe_1': '(SELECT distinct n FROM node0)',
                'node0': '(SELECT number % 2 n from numbers(100))',
            },
            'SELECT count() FROM (SELECT distinct n FROM (SELECT number % 2 n from numbers(100)) as node0) as test_pipe_1'
        )
    ]

    def test_replace(self):
        for (sql, replacements, expected_query) in self.scenarios:
            with self.subTest(sql=sql, replacements=replacements):
                self.assertEqual(replace_tables(sql, replacements), chquery.format(expected_query))

    def test_cycle(self):
        sql = 'select * from test'
        replacements = {
            'test': '(select * from test0)',
            'test0': '(select * from test_id inner join wadus using b)',
            'test_id': 'test_id_on_disk',
            'wadus': '(select * from foo where c < 1000)',  # <-----|
            'foo': '(select * from wadus)',  # cyclic dependency ---|
            'test_id_on_disk': '(select * from test_id_on_disk where a > 10)'
        }
        with self.assertRaisesRegex(ValueError, 'Circular dependencies exist'):
            replace_tables(sql, replacements)

    def test_other_database(self):
        sql = 'select * from nyc_taxi'
        replacements = {
            'nyc_taxi': '(select * from public.nyc_taxi)'
        }

        expected_query = 'select * from (select * from public.nyc_taxi) as nyc_taxi'

        replaced = replace_tables(sql, replacements)
        self.assertEqual(replaced, chquery.format(expected_query))

    def test_other_database_with_tuple(self):
        sql = 'select * from nyc_taxi'
        replacements = {
            'nyc_taxi': ('public', 'nyc_taxi')
        }

        expected_query = 'select * from public.nyc_taxi'

        replaced = replace_tables(sql, replacements)
        self.assertEqual(replaced, chquery.format(expected_query))

    def test_join_get(self):
        replacements = {
            'abcd': 't_id_abcd'
        }
        expected_query = "select joinGet('t_id_abcd', 'test', 1)"
        replaced = replace_tables("select joinGet('abcd', 'test', 1)", replacements)
        self.assertEqual(replaced, chquery.format(expected_query))

        expected_query = "select joinGet(t_id_abcd, 'test', 1)"
        replaced = replace_tables("select joinGet(abcd, 'test', 1)", replacements)
        self.assertEqual(replaced, chquery.format(expected_query))

    def test_join_get_tuple(self):
        replacements = {
            'abcd': ('db_1', 't_id_abcd')
        }

        expected_query = "select joinGet('db_1.t_id_abcd', 'test', 1)"
        replaced = replace_tables("select joinGet('abcd', 'test', 1)", replacements)
        self.assertEqual(replaced, chquery.format(expected_query))

        expected_query = "select joinGet(db_1.t_id_abcd, 'test', 1)"
        replaced = replace_tables("select joinGet(abcd, 'test', 1)", replacements)
        self.assertEqual(replaced, chquery.format(expected_query))

    def test_join_get_default_database(self):
        replacements = {
            'abcd': 't_id_abcd'
        }

        expected_query = "select joinGet('d_012345.t_id_abcd', 'test', 1)"
        replaced = replace_tables("select joinGet('abcd', 'test', 1)", replacements, default_database='d_012345')
        self.assertEqual(replaced, chquery.format(expected_query))

        expected_query = "select joinGet(d_012345.t_id_abcd, 'test', 1)"
        replaced = replace_tables("select joinGet(abcd, 'test', 1)", replacements, default_database='d_012345')
        self.assertEqual(replaced, chquery.format(expected_query))

    def test_join_get_nested(self):
        replacements = {
            't1': 't_id_1',
            't2': 't_id_2',
            't3': 't_id_3',
        }
        expected_query = "SELECT joinGet('d_012345.t_id_1', 'c1', concat(joinGet('d_012345.t_id_2', 'c2', i2), '_', joinGet('d_012345.t_id_3', 'c3', i3), '_', 'label'))"
        replaced = replace_tables("SELECT joinGet('t1', 'c1', concat(joinGet('t2', 'c2', i2), '_', joinGet('t3', 'c3', i3), '_', 'label'))", replacements, default_database='d_012345')
        self.assertEqual(replaced, chquery.format(expected_query))

    def test_join_nested_2(self):
        replacements = {
            'blabla': 'alibaba',
            'pp': 't_pp_01'
        }
        query = "select joinGet(blabla, 'a', joinGet(pp, 'b', c))"
        replaced = replace_tables(query, replacements, default_database='d_012345')
        expected_query = "select joinGet(d_012345.alibaba, 'a', joinGet(d_012345.t_pp_01, 'b', c))"
        self.assertEqual(replaced, chquery.format(expected_query))

    def test_invalid_subquery(self):
        sql = """SELECT * FROM clients"""
        replacements = {
            'clients': "(select * from clients where country 'ES')",
        }

        with self.assertRaisesRegex(ValueError, r'Syntax error'):
            replace_tables(sql, replacements)
