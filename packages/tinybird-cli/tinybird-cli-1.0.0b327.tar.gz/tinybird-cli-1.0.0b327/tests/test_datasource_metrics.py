
from io import StringIO
import uuid
import tornado
import pytest

from tests.views.base_test import BaseTest, TBApiProxyAsync
from tests_e2e.aux import poll_async
from tinybird.constants import CHCluster
from tinybird.datasource_metrics import DataSourceMetrics

from tinybird.job import UsageMetricsTracker
from tinybird.token_scope import scopes
from tinybird.user import User, Users, public

from tests.conftest import is_main_process


@pytest.mark.serial  # Direct access to the public user
@pytest.mark.skipif(not is_main_process(), reason="Serial test")
class TestDataSourceMetrics(BaseTest):
    def setUp(self):
        super(TestDataSourceMetrics, self).setUp()
        self.original_user_get_all = User.get_all
        self.tb_api_proxy_async = TBApiProxyAsync(self)
        self.usage_metrics_tracker = UsageMetricsTracker()
        self.public_user = public.get_public_user()
        self.usage_metrics_storage = self.public_user.get_datasource('usage_metrics_storage__v2')
        self.interval = 60 * 60 * 24 * 7

    @tornado.testing.gen_test
    async def test_get_storage_metric(self):
        cluster = CHCluster('tinybird', User.default_database_server)
        workspace_name = f"test_get_total_rows_metric_{uuid.uuid4().hex}"
        email = f'{workspace_name}@example.com'
        workspace = await self.tb_api_proxy_async.register_user_and_workspace(email, workspace_name, cluster)
        token = Users.get_token_for_scope(workspace, scopes.ADMIN)
        self.workspaces_to_delete.append(workspace)

        datasource_name = 'ds_test_get_storage_metric'
        await self.tb_api_proxy_async.create_datasource_from_data(
            token=token,
            ds_name=datasource_name,
            data=StringIO("d,sales\n2019-01-01,2\n2019-01-02,3")
        )
        datasource = Users.get_datasource(workspace, datasource_name)

        # wait for replication before tracking storage
        self.wait_for_datasource_replication(workspace, datasource)

        self.usage_metrics_tracker.track_usage_metrics_storage(
            self.public_user,
            [User.get_by_id(workspace.id)]
        )
        self.wait_for_public_table_replication('usage_metrics_storage__v2')
        metric_type = 'storage'
        datasource_metrics = DataSourceMetrics(workspace, datasource, metric_type, self.interval)
        metric = await datasource_metrics.get_metric()
        assert metric['data'][-1][metric_type] > 0
        assert metric['ticks'] == (self.interval / (60 * 60 * 24)) + 1

    @tornado.testing.gen_test
    async def test_get_total_rows_metric(self):
        cluster = CHCluster('tinybird', User.default_database_server)
        workspace_name = f"test_get_total_rows_metric_{uuid.uuid4().hex}"
        email = f'{workspace_name}@example.com'
        workspace = await self.tb_api_proxy_async.register_user_and_workspace(email, workspace_name, cluster)
        token = Users.get_token_for_scope(workspace, scopes.ADMIN)
        self.workspaces_to_delete.append(workspace)
        datasource_name = 'ds_test_get_total_rows_metric'
        await self.tb_api_proxy_async.create_datasource_from_data(
            token=token,
            ds_name=datasource_name,
            data=StringIO("d,sales\n2019-01-01,2\n2019-01-02,3")
        )
        datasource = Users.get_datasource(workspace, datasource_name)

        # wait for replication before tracking storage
        self.wait_for_datasource_replication(workspace, datasource)

        self.usage_metrics_tracker.track_usage_metrics_storage(
            self.public_user,
            [User.get_by_id(workspace.id)]
        )
        self.wait_for_public_table_replication('usage_metrics_storage__v2')
        metric_type = 'total_rows'
        datasource_metrics = DataSourceMetrics(workspace, datasource, metric_type, self.interval)
        metric = await datasource_metrics.get_metric()
        assert metric['data'][-1][metric_type] == 2
        assert metric['ticks'] == (self.interval / (60 * 60 * 24)) + 1

    @tornado.testing.gen_test
    async def test_get_new_rows_metric(self):
        cluster = CHCluster('tinybird', User.default_database_server)
        workspace_name = f"test_get_new_rows_metric_{uuid.uuid4().hex}"
        email = f'{workspace_name}@example.com'
        workspace = await self.tb_api_proxy_async.register_user_and_workspace(email, workspace_name, cluster)
        token = Users.get_token_for_scope(workspace, scopes.ADMIN)
        self.workspaces_to_delete.append(workspace)
        datasource_name = 'ds_test_get_new_rows_metric'
        await self.tb_api_proxy_async.create_datasource_from_data(
            token=token,
            ds_name=datasource_name,
            data=StringIO("d,sales\n2019-01-01,2\n2019-01-02,3")
        )
        datasource = Users.get_datasource(workspace, datasource_name)

        # wait for replication before tracking storage
        self.wait_for_datasource_replication(workspace, datasource)

        self.wait_for_public_table_replication('datasources_ops_log')
        metric_type = 'new_rows'
        datasource_metrics = DataSourceMetrics(workspace, datasource, metric_type, self.interval)

        async def f():
            metric = await datasource_metrics.get_metric()
            assert metric['data'][-1][metric_type] == 2
            assert metric['ticks'] == (self.interval / (60 * 60 * 24)) + 1

        await poll_async(f)

    @tornado.testing.gen_test
    async def test_get_new_rows_quarantine_metric(self):
        cluster = CHCluster('tinybird', User.default_database_server)
        workspace_name = f"test_get_new_rows_quarantine_metric_{uuid.uuid4().hex}"
        email = f'{workspace_name}@example.com'
        workspace = await self.tb_api_proxy_async.register_user_and_workspace(email, workspace_name, cluster)
        token = Users.get_token_for_scope(workspace, scopes.ADMIN)
        self.workspaces_to_delete.append(workspace)
        datasource_name = 'ds_test_get_new_rows_metric'
        await self.tb_api_proxy_async.create_datasource_from_data(
            token=token,
            ds_name=datasource_name,
            data=StringIO("d,sales\n2019-01-01,2\n2019-01-02,3")
        )
        await self._insert_data_in_datasource(
            token=token,
            ds_name=datasource_name,
            data="1,2,3\n4,5,6\n7,8,9",
            assert_response=False
        )
        datasource = Users.get_datasource(workspace, datasource_name)

        # wait for replication before tracking storage
        self.wait_for_datasource_replication(workspace, datasource)

        self.wait_for_public_table_replication('datasources_ops_log')
        metric_type = 'new_rows_quarantine'
        datasource_metrics = DataSourceMetrics(workspace, datasource, metric_type, self.interval)

        async def f():
            metric = await datasource_metrics.get_metric()
            assert metric['data'][-1][metric_type] == 3
            assert metric['ticks'] == (self.interval / (60 * 60 * 24)) + 1

        await poll_async(f)
