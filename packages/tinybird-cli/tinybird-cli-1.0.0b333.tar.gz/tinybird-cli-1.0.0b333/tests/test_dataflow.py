import tornado

from tests.views.test_api_datasources import TestAPIDatasourceBase

from tinybird.user import User, Users, UserAccount
from tinybird.token_scope import scopes
from tinybird.dataflow import DataFlow
from tinybird.feature_flags import FeatureFlagWorkspaces


class TestDataFlow(TestAPIDatasourceBase):
    def setUp(self):
        super(TestDataFlow, self).setUp()
        self.user_account = UserAccount.get_by_id(self.USER_ID)
        self.workspace = User.get_by_id(self.WORKSPACE_ID)
        self.token = Users.add_token(self.workspace, "test", scopes.ADMIN)
        with User.transaction(self.WORKSPACE_ID) as w:
            w.feature_flags[FeatureFlagWorkspaces.EXPORT.value] = True
            self.workspace = w

    def tearDown(self):
        with User.transaction(self.WORKSPACE_ID) as w:
            w.feature_flags[FeatureFlagWorkspaces.EXPORT.value] = False
            self.workspace = w
        super(TestDataFlow, self).tearDown()

    async def _setup_cascade(self, has_incompatible_partitions: bool = False):
        """
        +---------+  MV1to2   +-----+  MV2to4   +-----+
        |   DS1   | --------> | DS2 | --------> | DS4 |
        +---------+           +-----+           +-----+
            |
            | MV1to3
            v
        +---------+  MV3to5   +-----+
        |   DS3   | --------> | DS5 |
        +---------+           +-----+
        """

        ds1 = 'DS1'
        await self.create_datasource_async(self.token, ds1, """
                    dt Date,
                    country String,
                    product String,
                    units Int32
                """, {'engine': 'MergeTree', 'engine_partition_key': 'dt', 'engine_sorting_key': 'country, dt, product'})

        ds2 = 'DS2'
        await self.create_datasource_async(self.token, ds2, """
                    dt Date,
                    country String,
                    product String,
                    sum_units Int32
                """, {'engine': 'SummingMergeTree', 'engine_partition_key': 'dt', 'engine_sorting_key': 'country, dt, product'})

        await self.create_view_async(self.workspace, self.token, ds2, f"""
                SELECT
                    dt,
                    country,
                    product,
                    toInt32(sum(units)) AS sum_units
                FROM {ds1}
                WHERE product = 'A'
                GROUP BY dt, country, product
                """, pipe_name='MV1to2')

        ds4 = 'DS4'
        await self.create_datasource_async(self.token, ds4, """
                    dt Date,
                    country String,
                    sum_per_country Int32
                """, {'engine': 'SummingMergeTree', 'engine_partition_key': 'dt', 'engine_sorting_key': 'country, dt'})

        await self.create_view_async(self.workspace, self.token, ds4, f"""
                SELECT
                    dt,
                    country,
                    toInt32(sum(sum_units)) AS sum_per_country
                FROM {ds2}
                GROUP BY dt, country
                """, pipe_name='MV2to4')

        ds3 = 'DS3'
        if has_incompatible_partitions:
            engine = {'engine': 'SummingMergeTree', 'engine_sorting_key': 'country, dt, product'}
        else:
            engine = {'engine': 'SummingMergeTree', 'engine_partition_key': 'dt', 'engine_sorting_key': 'country, dt, product'}

        await self.create_datasource_async(self.token, ds3, """
                    dt Date,
                    country String,
                    product String,
                    sum_units Int32
                """, engine)

        await self.create_view_async(self.workspace, self.token, ds3, f"""
                SELECT
                    dt,
                    country,
                    product,
                    toInt32(sum(units)) AS sum_units
                FROM {ds1}
                WHERE product = 'B'
                GROUP BY dt, country, product
                """, pipe_name='MV1to3')

        ds5 = 'DS5'
        await self.create_datasource_async(self.token, ds5, """
                    dt Date,
                    country String,
                    sum_per_country Int32
                """, {'engine': 'SummingMergeTree', 'engine_partition_key': 'dt', 'engine_sorting_key': 'country, dt'})

        await self.create_view_async(self.workspace, self.token, ds5, f"""
                SELECT
                    dt,
                    country,
                    toInt32(sum(sum_units)) AS sum_per_country
                FROM {ds3}
                GROUP BY dt, country
                """, pipe_name='MV3to5')

        return ds1, ds2, ds3, ds4, ds5

    async def _setup_cascade_from_copy(self, has_incompatible_partitions: bool = False):
        """
        +---------+   copy   +-----+  MV2to4   +-----+
        |   DS1   | -------> | DS2 | --------> | DS4 |
        +---------+          +-----+           +-----+
                                |
                                | MV2to3
                                v
                            +---------+  MV3to5   +-----+
                            |   DS3   | --------> | DS5 |
                            +---------+           +-----+
        """

        ds1 = 'DS1'
        await self.create_datasource_async(self.token, ds1, """
                    dt Date,
                    country String,
                    product String,
                    units Int32
                """, {'engine': 'MergeTree', 'engine_partition_key': 'dt', 'engine_sorting_key': 'country, dt, product'})

        ds2 = 'DS2'
        await self.create_datasource_async(self.token, ds2, """
                    dt Date,
                    country String,
                    product String,
                    sum_units Int32
                """, {'engine': 'SummingMergeTree', 'engine_partition_key': 'dt', 'engine_sorting_key': 'country, dt, product'})

        copy_pipe = f'{ds2}_copy'
        await self.create_pipe_copy_async(self.workspace, self.token, ds2, copy_pipe, ds1, f"""
                SELECT
                    dt,
                    country,
                    product,
                    toInt32(sum(units)) AS sum_units
                FROM {ds1}
                WHERE product = 'A'
                GROUP BY dt, country, product
            """)

        ds4 = 'DS4'
        await self.create_datasource_async(self.token, ds4, """
                    dt Date,
                    country String,
                    sum_per_country Int32
                """, {'engine': 'SummingMergeTree', 'engine_partition_key': 'dt', 'engine_sorting_key': 'country, dt'})

        await self.create_view_async(self.workspace, self.token, ds4, f"""
                SELECT
                    dt,
                    country,
                    toInt32(sum(sum_units)) AS sum_per_country
                FROM {ds2}
                GROUP BY dt, country
                """, pipe_name='MV2to4')

        ds3 = 'DS3'
        if has_incompatible_partitions:
            engine = {'engine': 'SummingMergeTree', 'engine_sorting_key': 'country, dt, product'}
        else:
            engine = {'engine': 'SummingMergeTree', 'engine_partition_key': 'dt', 'engine_sorting_key': 'country, dt, product'}

        await self.create_datasource_async(self.token, ds3, """
                    dt Date,
                    country String,
                    product String,
                    sum_units Int64
                """, engine)

        await self.create_view_async(self.workspace, self.token, ds3, f"""
                SELECT
                    dt,
                    country,
                    product,
                    sum(sum_units) as sum_units
                FROM {ds2}
                WHERE product = 'B'
                GROUP BY country, dt, product
                """, pipe_name='MV2to3')

        ds5 = 'DS5'
        await self.create_datasource_async(self.token, ds5, """
                    dt Date,
                    country String,
                    sum_per_country Int32
                """, {'engine': 'SummingMergeTree', 'engine_partition_key': 'dt', 'engine_sorting_key': 'country, dt'})

        await self.create_view_async(self.workspace, self.token, ds5, f"""
                SELECT
                    dt,
                    country,
                    toInt32(sum(sum_units)) AS sum_per_country
                FROM {ds3}
                GROUP BY dt, country
                """, pipe_name='MV3to5')

        return ds1, ds2, ds3, ds4, ds5, copy_pipe

    @tornado.testing.gen_test
    async def test_get_steps_happy_case(self):
        ds1, ds2, ds3, ds4, ds5 = await self._setup_cascade()
        datasource_1 = Users.get_datasource(self.workspace, ds1)
        datasource_2 = Users.get_datasource(self.workspace, ds2)
        datasource_3 = Users.get_datasource(self.workspace, ds3)
        datasource_4 = Users.get_datasource(self.workspace, ds4)
        datasource_5 = Users.get_datasource(self.workspace, ds5)

        steps, skipped = DataFlow.get_steps(self.workspace, datasource_1, skip_incompatible_partitions=False)

        step_datasources = [step.step_datasource.id for step in steps]
        self.assertTrue(datasource_2.id in step_datasources)
        self.assertTrue(datasource_3.id in step_datasources)
        self.assertTrue(datasource_4.id in step_datasources)
        self.assertTrue(datasource_5.id in step_datasources)
        self.assertTrue(skipped == [])

    @tornado.testing.gen_test
    async def test_get_steps_skip_incompatible_partitions(self):
        ds1, ds2, ds3, ds4, _ds5 = await self._setup_cascade(has_incompatible_partitions=True)
        datasource_1 = Users.get_datasource(self.workspace, ds1)
        datasource_2 = Users.get_datasource(self.workspace, ds2)
        datasource_3 = Users.get_datasource(self.workspace, ds3)
        datasource_4 = Users.get_datasource(self.workspace, ds4)

        steps, skipped = DataFlow.get_steps(self.workspace, datasource_1, skip_incompatible_partitions=True)

        step_datasources = [step.step_datasource.id for step in steps]
        skipped_datasources = [step.step_datasource.id for step in skipped]

        self.assertTrue(datasource_2.id in step_datasources)
        self.assertTrue(datasource_4.id in step_datasources)
        self.assertTrue(datasource_3.id in skipped_datasources)

    @tornado.testing.gen_test
    async def test_get_steps_with_copy_happy_case(self):
        _, ds2, ds3, ds4, ds5, copy_pipe = await self._setup_cascade_from_copy()

        datasource_2 = Users.get_datasource(self.workspace, ds2)
        datasource_3 = Users.get_datasource(self.workspace, ds3)
        datasource_4 = Users.get_datasource(self.workspace, ds4)
        datasource_5 = Users.get_datasource(self.workspace, ds5)

        pipe = Users.get_pipe(self.workspace, copy_pipe)

        steps, skipped = DataFlow.get_steps(
            source_workspace=self.workspace,
            source_datasource=datasource_2,
            source_pipe=pipe,
            skip_incompatible_partitions=False)

        step_datasources = [step.step_datasource.id for step in steps]
        self.assertTrue(datasource_2.id in step_datasources)
        self.assertTrue(datasource_3.id in step_datasources)
        self.assertTrue(datasource_4.id in step_datasources)
        self.assertTrue(datasource_5.id in step_datasources)
        self.assertTrue(skipped == [])

    @tornado.testing.gen_test
    async def test_get_steps_with_copy_skip_incompatible_partitions(self):
        _, ds2, ds3, ds4, ds5, copy_pipe = await self._setup_cascade_from_copy(has_incompatible_partitions=True)

        datasource_2 = Users.get_datasource(self.workspace, ds2)
        datasource_3 = Users.get_datasource(self.workspace, ds3)
        datasource_4 = Users.get_datasource(self.workspace, ds4)

        pipe = Users.get_pipe(self.workspace, copy_pipe)

        steps, skipped = DataFlow.get_steps(
            source_workspace=self.workspace,
            source_datasource=datasource_2,
            source_pipe=pipe,
            skip_incompatible_partitions=True)

        skipped_datasources = [step.step_datasource.id for step in skipped]
        step_datasources = [step.step_datasource.id for step in steps]

        self.assertTrue(datasource_2.id in step_datasources)
        self.assertTrue(datasource_4.id in step_datasources)
        self.assertTrue(datasource_3.id in skipped_datasources)
