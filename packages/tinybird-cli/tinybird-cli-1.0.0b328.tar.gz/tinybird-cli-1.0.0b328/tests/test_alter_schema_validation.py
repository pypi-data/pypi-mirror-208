import tinybird.user
from tinybird.table import alter_table_operations
from tinybird.user import Users
from .views.base_test import BaseTest

import tornado.testing


class TestAlterSchemaValidation(BaseTest):

    def setUp(self):
        super(TestAlterSchemaValidation, self).setUp()
        self.workspace = Users.get_by_id(self.WORKSPACE_ID)

    @tornado.testing.gen_test
    async def test_same_schema(self):
        schema_a = """
            a String CODEC(LZ4HC(2)),
            b Float64,
            c Float32
        """
        schema_b = schema_a
        operations, operations_quarantine = await alter_table_operations(self.workspace, schema_a, schema_b)
        self.assertEqual(operations, [])
        self.assertEqual(operations_quarantine, [])

    @tornado.testing.gen_test
    async def test_add_column(self):
        schema_a = """
            a String CODEC(LZ4HC(2)),
            b Float64,
            c Float32
        """
        schema_b = """
            a String CODEC(LZ4HC(2)),
            b Float64,
            c Float32,
            d String
        """
        operations, operations_quarantine = await alter_table_operations(self.workspace, schema_a, schema_b)
        self.assertEqual(operations, ['ADD COLUMN `d` String'])
        self.assertEqual(operations_quarantine, ['ADD COLUMN `d` Nullable(String)'])

    @tornado.testing.gen_test
    async def test_MATERIALIZED_replace(self):
        schema_a = """
            a String CODEC(LZ4HC(2)),
            b Float64,
            c Float32
        """
        schema_b = """
            a String CODEC(LZ4HC(2)),
            b Float64,
            c Float32,
            d String MATERIALIZED joinGet(other_database.other_table, 'val', toUInt32(b))
        """
        with self.assertRaisesRegex(tinybird.user.QueryNotAllowed, r"Resource 'other_database.other_table' not found"):
            await alter_table_operations(self.workspace, schema_a, schema_b)

        schema_c = """
            a String CODEC(LZ4HC(2)),
            b Float64,
            c Float32,
            d String MATERIALIZED a IN (Select name from remote('127.0.0.1', 'system.tables'))
        """
        with self.assertRaisesRegex(tinybird.user.QueryNotAllowed, "DB::Exception: Usage of function remote is restricted"):
            await alter_table_operations(self.workspace, schema_a, schema_c)

    @tornado.testing.gen_test
    async def test_ALIAS_replace(self):
        schema_a = """
            a String CODEC(LZ4HC(2)),
            b Float64,
            c Float32
        """
        schema_b = """
            a String CODEC(LZ4HC(2)),
            b Float64,
            c Float32,
            d String ALIAS joinGet(other_database.other_table, 'val', toUInt32(b))
        """
        with self.assertRaisesRegex(ValueError, r"ALIAS not supported"):
            await alter_table_operations(self.workspace, schema_a, schema_b)

        schema_c = """
            a String CODEC(LZ4HC(2)),
            b Float64,
            c Float32,
            d String ALIAS a IN (Select name from remote('127.0.0.1', 'system.tables'))
        """
        with self.assertRaisesRegex(ValueError, r"ALIAS not supported"):
            await alter_table_operations(self.workspace, schema_a, schema_c)

    @tornado.testing.gen_test
    async def test_DEFAULT_replace(self):
        schema_a = """
            a String CODEC(LZ4HC(2)),
            b Float64,
            c Float32
        """
        schema_b = """
            a String CODEC(LZ4HC(2)),
            b Float64,
            c Float32,
            d String DEFAULT joinGet(other_database.other_table, 'val', toUInt32(b))
        """
        with self.assertRaisesRegex(tinybird.user.QueryNotAllowed, r"Resource 'other_database.other_table' not found"):
            await alter_table_operations(self.workspace, schema_a, schema_b)

        schema_c = """
            a String CODEC(LZ4HC(2)),
            b Float64,
            c Float32,
            d String DEFAULT a IN (Select name from remote('127.0.0.1', 'system.tables'))
        """
        with self.assertRaisesRegex(tinybird.user.QueryNotAllowed, "DB::Exception: Usage of function remote is restricted"):
            await alter_table_operations(self.workspace, schema_a, schema_c)

    @tornado.testing.gen_test
    async def test_add_several_columns(self):

        schema_a = """
            a String CODEC(LZ4HC(2)),
            b Float64,
            c Float32
        """
        schema_b = """
            a String CODEC(LZ4HC(2)),
            b Float64,
            c Float32,
            d LowCardinality(String),
            e Int8 DEFAULT(0),
            f Nullable(Int32)
        """
        operations, operations_quarantine = await alter_table_operations(self.workspace, schema_a, schema_b)
        expected_ops = [
            'ADD COLUMN `d` LowCardinality(String)',
            'ADD COLUMN `e` Int8 DEFAULT 0',
            'ADD COLUMN `f` Nullable(Int32)',
        ]
        expected_quarantine_ops = [
            'ADD COLUMN `d` Nullable(String)',
            'ADD COLUMN `e` Nullable(String)',
            'ADD COLUMN `f` Nullable(String)',
        ]
        self.assertEqual(operations, expected_ops)
        self.assertEqual(operations_quarantine, expected_quarantine_ops)

    @tornado.testing.gen_test
    async def test_add_column_not_at_the_end(self):
        schema_a = """
            a String CODEC(LZ4HC(2)),
            b Float64,
            c Float32
        """
        schema_b = """
            aa Float32,
            aa2 String CODEC(LZ4HC(2)),
            a String CODEC(LZ4HC(2)),
            b Float64,
            c Float32
        """
        operations, operations_quarantine = await alter_table_operations(self.workspace, schema_a, schema_b)
        expected_ops = [
            'ADD COLUMN `aa` Float32 FIRST',
            'ADD COLUMN `aa2` String CODEC(LZ4HC(2)) AFTER aa',
        ]
        expected_quarantine_ops = [
            'ADD COLUMN `aa` Nullable(String) FIRST',
            'ADD COLUMN `aa2` Nullable(String) AFTER aa',
        ]
        self.assertEqual(operations, expected_ops)
        self.assertEqual(operations_quarantine, expected_quarantine_ops)

    @tornado.testing.gen_test
    async def test_add_columns_in_the_middle(self):
        schema_a = """
            a String CODEC(LZ4HC(2)),
            b Float64,
            c Float32
        """
        schema_b = """
            a String CODEC(LZ4HC(2)),
            a1 Float32,
            a2 String CODEC(LZ4HC(2)),
            b Float64,
            c Float32
        """
        operations, operations_quarantine = await alter_table_operations(self.workspace, schema_a, schema_b)
        expected_ops = [
            'ADD COLUMN `a1` Float32 AFTER a',
            'ADD COLUMN `a2` String CODEC(LZ4HC(2)) AFTER a1',
        ]
        expected_quarantine_ops = [
            'ADD COLUMN `a1` Nullable(String) AFTER a',
            'ADD COLUMN `a2` Nullable(String) AFTER a1',
        ]
        self.assertEqual(operations, expected_ops)
        self.assertEqual(operations_quarantine, expected_quarantine_ops)

    @tornado.testing.gen_test
    async def test_add_columns_in_the_middle_in_the_end(self):
        schema_a = """
            a String CODEC(LZ4HC(2)),
            b Float64,
            c Float32
        """
        schema_b = """
            a0 String,
            a String CODEC(LZ4HC(2)),
            a1 String,
            b Float64,
            b1 String,
            c Float32,
            c1 String
        """
        operations, operations_quarantine = await alter_table_operations(self.workspace, schema_a, schema_b)
        expected_ops = [
            'ADD COLUMN `a0` String FIRST',
            'ADD COLUMN `a1` String AFTER a',
            'ADD COLUMN `b1` String AFTER b',
            'ADD COLUMN `c1` String AFTER c',
        ]
        expected_quarantine_ops = [
            'ADD COLUMN `a0` Nullable(String) FIRST',
            'ADD COLUMN `a1` Nullable(String) AFTER a',
            'ADD COLUMN `b1` Nullable(String) AFTER b',
            'ADD COLUMN `c1` Nullable(String) AFTER c',
        ]
        self.assertEqual(operations, expected_ops)
        self.assertEqual(operations_quarantine, expected_quarantine_ops)

    @tornado.testing.gen_test
    async def test_drop_column(self):
        schema_a = """
            a String CODEC(LZ4HC(2)),
            b Float64,
            c Float32
        """
        schema_b = """
            a String CODEC(LZ4HC(2)),
            b Float64
        """
        with self.assertRaisesRegex(ValueError, r"Dropping the 'c' column is not supported"):
            await alter_table_operations(self.workspace, schema_a, schema_b)

    @tornado.testing.gen_test
    async def test_add_and_drop_columns(self):
        schema_a = """
            a String CODEC(LZ4HC(2)),
            b Float64,
            c Float32
        """
        schema_b = """
            a String CODEC(LZ4HC(2)),
            b Float64,
            d String
        """
        with self.assertRaisesRegex(ValueError, r"Dropping the 'c' column is not supported"):
            await alter_table_operations(self.workspace, schema_a, schema_b)

    @tornado.testing.gen_test
    async def test_modified_column(self):
        schema_a = """
            a String CODEC(LZ4HC(2)),
            b Float64,
            c Float32
        """
        schema_b = """
            a String CODEC(LZ4HC(2)),
            b String,
            c Float32
        """
        with self.assertRaisesRegex(ValueError, r"Modifying the 'b' column is not supported. Changing from '`b` Float64' to '`b` String'"):
            await alter_table_operations(self.workspace, schema_a, schema_b)
