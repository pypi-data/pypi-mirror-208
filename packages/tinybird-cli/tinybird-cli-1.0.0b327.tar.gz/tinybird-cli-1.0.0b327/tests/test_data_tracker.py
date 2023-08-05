from datetime import datetime
from io import StringIO
from unittest.mock import patch

import pytest
import tornado
import uuid

from tests.utils import exec_sql
from tests.views.base_test import BaseTest, TBApiProxy, TBApiProxyAsync
from tinybird.job import WorkspaceDatabaseUsageTracker, UsageMetricsTracker
from tinybird.user import public, User, UserAccount, Users
from tinybird.user_workspace import UserWorkspaceRelationship
from tinybird.constants import Relationships
from tinybird.token_scope import scopes
from tinybird.ch import ch_create_table_as_table

from tests.conftest import is_main_process


@pytest.mark.serial  # Direct access to the public user
@pytest.mark.skipif(not is_main_process(), reason="Serial test")
class TestDataTracker(BaseTest):

    def setUp(self):
        super(TestDataTracker, self).setUp()
        self.original_user_get_all = User.get_all
        self.original_user_account_get_all = UserAccount.get_all
        self.original_relationships_get_all = UserWorkspaceRelationship.get_all

        self.tb_api_proxy = TBApiProxy(self)
        public_user = public.get_public_user()
        token = public_user.get_token_for_scope(scopes.ADMIN)
        self.tb_api_proxy.truncate_datasource(token, 'user_accounts_all')
        self.tb_api_proxy.truncate_datasource(token, 'workspaces_all')
        self.tb_api_proxy.truncate_datasource(token, 'user_workspaces_all')

    def tearDown(self):
        User.get_all = self.original_user_get_all
        UserAccount.get_all = self.original_user_account_get_all
        UserWorkspaceRelationship.get_all = self.original_relationships_get_all
        super(TestDataTracker, self).tearDown()

    def _execute_tracker_mocking_get_alls(self, user_get_all=None, user_account_get_all=None, relationships_get_all=None):

        if user_get_all:
            User.get_all = user_get_all

        if user_account_get_all:
            UserAccount.get_all = user_account_get_all

        if relationships_get_all:
            UserWorkspaceRelationship.get_all = relationships_get_all

        data_tracker = WorkspaceDatabaseUsageTracker()
        data_tracker.start()
        data_tracker.terminate()
        data_tracker.join()

    def test_data_tracker_updates_workspace_info(self):
        pu = public.get_public_user()
        workspaces_all_ds = pu.get_datasource('workspaces_all')

        created_at = datetime.now()
        self._execute_tracker_mocking_get_alls(user_get_all=lambda: [
            User(id='1234', name="1234_name", database="1234_database", database_server="1234_database_server",
                 created_at=created_at, origin=None)
        ])

        content = exec_sql(pu.database, f"select * from {workspaces_all_ds.id} FORMAT JSON")
        self.assertEqual(content['data'], [{'id': '1234', 'name': '1234_name', 'database': '1234_database', 'database_server': '1234_database_server', 'plan': 'dev', 'deleted': 0, 'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S'), 'origin': ''}])

        created_at = datetime.now()
        self._execute_tracker_mocking_get_alls(user_get_all=lambda: [
            User(id='5678', name="5678_name", database="5678_database", database_server="5678_database_server",
                 created_at=created_at, origin='8765')
        ])

        content = exec_sql(pu.database, f"select * from {workspaces_all_ds.id} FORMAT JSON")

        self.assertEqual(len(content['data']), 2)

        # Check ReplacingMergeTree merges correctly
        created_at = datetime.now()
        self._execute_tracker_mocking_get_alls(user_get_all=lambda: [
            User(id='5678', name="5678_name", database="5678_database", database_server="5678_database_server",
                 created_at=created_at, origin='8765')
        ])
        self.assertEqual(len(content['data']), 2)

    def test_data_tracker_correctly_writes_user_accounts(self):
        pu = public.get_public_user()
        user_accounts_ds = pu.get_datasource('user_accounts_all')

        created_at = datetime.now()
        self._execute_tracker_mocking_get_alls(user_account_get_all=lambda: [
            UserAccount(id='useracc1', email="useracc1_email", created_at=created_at)
        ])

        content = exec_sql(pu.database, f"select * from {user_accounts_ds.id} FORMAT JSON")
        self.assertEqual(content['data'], [{'id': 'useracc1', 'email': 'useracc1_email', 'feature_flags': '{}', 'deleted': 0, 'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S')}])

    def test_data_tracker_correctly_writes_user_workspaces(self):
        pu = public.get_public_user()
        user_workspaces_ds = pu.get_datasource('user_workspaces_all')

        created_at = datetime.now()
        self._execute_tracker_mocking_get_alls(relationships_get_all=lambda: [
            UserWorkspaceRelationship(id="rel_id", user_id='rel_user_id', workspace_id="rel_works_id", relationship=Relationships.ADMIN, created_at=created_at)
        ])

        content = exec_sql(pu.database, f"select * from {user_workspaces_ds.id} FORMAT JSON")
        self.assertEqual(content['data'], [{'id': 'rel_id', 'relationship': 'admin', 'user_id': 'rel_user_id', 'workspace_id': 'rel_works_id', 'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S')}])

    def test_data_tracker_correctly_writes_database_usage(self):
        pu = public.get_public_user()
        db_usage_ds = pu.get_datasource('db_usage')

        self._execute_tracker_mocking_get_alls()

        content = exec_sql(pu.database, f"select count(*) as total from {db_usage_ds.id} FORMAT JSON")
        self.assertGreater(int(content['data'][0]['total']), 0)


class TestUsageMetricsTracker(BaseTest):

    def setUp(self):
        super(TestUsageMetricsTracker, self).setUp()
        self.test_workspace = User.get_by_id(self.WORKSPACE_ID)
        self.test_user = UserAccount.get_by_id(self.USER_ID)
        self.tb_api_proxy_async = TBApiProxyAsync(self)

    @tornado.testing.gen_test
    @pytest.mark.skip(
        "usage_metrics_storage is going to be deprecated with https://gitlab.com/tinybird/analytics/-/issues/5280.")
    async def test_track_usage_metrics_storage(self):
        usage_metrics_tracker = UsageMetricsTracker()
        public_user = public.get_public_user()
        usage_metrics_storage = public_user.get_datasource('usage_metrics_storage')

        workspace_name = f"test_track_usage_{uuid.uuid4().hex}"
        email = f'{workspace_name}@example.com'
        workspace = await self.tb_api_proxy_async.register_user_and_workspace(email, workspace_name)
        self.workspaces_to_delete.append(workspace)
        token = Users.get_token_for_scope(workspace, scopes.ADMIN)

        await self.tb_api_proxy_async.create_datasource_from_data(
            token=token,
            ds_name='datasource_a',
            data=StringIO("d,sales\n2019-01-01,2\n2019-01-02,3")
        )
        await self.tb_api_proxy_async.create_datasource_from_data(
            token=token,
            ds_name='datasource_b',
            data=StringIO("d,sales\n2019-01-01,2\n2019-01-02,3")
        )

        datasource_a = Users.get_datasource(workspace, 'datasource_a')
        datasource_b = Users.get_datasource(workspace, 'datasource_b')
        self.wait_for_datasource_replication(workspace, datasource_a)
        self.wait_for_datasource_replication(workspace, datasource_b)

        usage_metrics_tracker.track_usage_metrics_storage(
            public_user,
            [User.get_by_id(workspace.id)]
        )

        self.wait_for_public_table_replication(usage_metrics_storage.name)
        content = exec_sql(public_user.database, f"select * from {usage_metrics_storage.id} FINAL WHERE database='{workspace.database}' FORMAT JSON")
        self.assertTrue(content['data'][0]['date'])
        self.assertTrue(content['data'][0]['database'] == workspace.database)
        self.assertEqual(int(content['data'][0]['rows']), 4)
        self.assertTrue(int(content['data'][0]['bytes_on_disk']) == pytest.approx(318, 50))

    @tornado.testing.gen_test
    async def test_track_usage_metrics_storage_v2(self):
        usage_metrics_tracker = UsageMetricsTracker()
        public_user = public.get_public_user()
        usage_metrics_storage = public_user.get_datasource('usage_metrics_storage__v2')

        workspace_name = f"test_track_usage_v2_{uuid.uuid4().hex}"
        email = f'{workspace_name}@example.com'
        workspace = await self.tb_api_proxy_async.register_user_and_workspace(email, workspace_name)
        user_account = UserAccount.get_by_email(email)
        token = Users.get_token_for_scope(workspace, scopes.ADMIN)
        self.workspaces_to_delete.append(workspace)

        await self.tb_api_proxy_async.create_datasource_from_data(
            token=token,
            ds_name='datasource_a',
            data=StringIO("d,sales\n2019-01-01,2\n2019-01-02,3")
        )
        ds_a = Users.get_datasource(workspace, 'datasource_a')
        await self.tb_api_proxy_async.create_datasource_from_data(
            token=token,
            ds_name='datasource_b',
            data=StringIO("d,sales\n2019-01-01,2\n2019-01-02,3")
        )
        ds_b = Users.get_datasource(workspace, 'datasource_b')

        self.wait_for_datasource_replication(workspace, ds_a)
        self.wait_for_datasource_replication(workspace, ds_b)

        # create and share to test_workspace a ds
        ws_to_share_name = f'workspace_to_share_{uuid.uuid4().hex}'
        workspace_to_share = await self.tb_api_proxy_async.register_user_and_workspace(f'{ws_to_share_name}@example.com', ws_to_share_name)
        user_to_share = UserAccount.get_by_email(f'{ws_to_share_name}@example.com')
        token_workspace_to_share = Users.get_token_for_scope(workspace_to_share, scopes.ADMIN_USER)
        token_user_to_share = UserAccount.get_token_for_scope(user_to_share, scopes.AUTH)
        self.workspaces_to_delete.append(workspace_to_share)

        token_workspace_to_share = Users.get_token_for_scope(workspace_to_share, scopes.ADMIN)

        datasource_to_share_in_workspace_to_share = await self.tb_api_proxy_async.create_datasource(
            token=token_workspace_to_share,
            ds_name='datasource_to_share',
            schema='col_a Int32,col_b Int32,col_c Int32'
        )

        await self.tb_api_proxy_async.invite_user_to_workspace(
            token=UserAccount.get_token_for_scope(user_account, scopes.AUTH),
            workspace_id=workspace.id,
            user_to_invite_email=user_to_share.email
        )

        await self.tb_api_proxy_async.share_datasource_with_another_workspace(
            token=token_user_to_share,
            datasource_id=datasource_to_share_in_workspace_to_share['datasource']['id'],
            origin_workspace_id=workspace_to_share.id,
            destination_workspace_id=workspace.id
        )

        usage_metrics_tracker.track_usage_metrics_storage(
            public_user,
            [User.get_by_id(workspace.id)]
        )

        self.wait_for_public_table_replication(usage_metrics_storage.name)
        content = exec_sql(public_user.database, f"select * from {usage_metrics_storage.id} FINAL WHERE user_id='{workspace.id}' FORMAT JSON")
        self.assertEqual(len(content['data']), 2)

        for row in content['data']:
            self.assertIn(row['datasource_id'], [ds_b.id, ds_a.id])
            self.assertTrue(row['timestamp'])
            self.assertTrue(row['user_id'] == workspace.id)
            self.assertEqual(int(row['rows']), 2)
            self.assertEqual(int(row['bytes']), pytest.approx(155, 25))
            self.assertEqual(int(row['rows_quarantine']), 0)
            self.assertEqual(int(row['bytes_quarantine']), 0)

    @tornado.testing.gen_test
    @pytest.mark.skip(
        "usage_metrics_storage is going to be deprecated with https://gitlab.com/tinybird/analytics/-/issues/5280.")
    async def test_track_usage_metrics_storage_counts_quarantine_rows(self):
        usage_metrics_tracker = UsageMetricsTracker()
        public_user = public.get_public_user()
        usage_metrics_storage = public_user.get_datasource('usage_metrics_storage')

        workspace_name = f"test_track_usage_quarantine_{uuid.uuid4().hex}"
        email = f'{workspace_name}@example.com'
        workspace = await self.tb_api_proxy_async.register_user_and_workspace(email, workspace_name)
        token = Users.get_token_for_scope(workspace, scopes.ADMIN)
        self.workspaces_to_delete.append(workspace)

        await self.tb_api_proxy_async.create_datasource_from_data(
            token=token,
            ds_name='datasource_a',
            data=StringIO("d,sales\n2019-01-01,2\n2019-01-02,3")
        )

        await self.tb_api_proxy_async.create_datasource_from_data(
            token=token,
            ds_name='datasource_a',
            data=StringIO("d,sales\nwrong_date,2\nwrong_date,3"),
            extra_params={'mode': 'append'}
        )
        ds_a = Users.get_datasource(workspace, 'datasource_a')

        self.wait_for_datasource_replication(workspace, ds_a, quarantine=True)

        usage_metrics_tracker.track_usage_metrics_storage(
            public_user,
            [User.get_by_id(workspace.id)]
        )

        self.wait_for_public_table_replication(usage_metrics_storage.name)
        content = exec_sql(public_user.database, f"select * from {usage_metrics_storage.id} FINAL WHERE database='{workspace.database}' FORMAT JSON")

        self.assertTrue(content['data'][0]['date'])
        self.assertTrue(content['data'][0]['database'] == workspace.database)
        self.assertEqual(int(content['data'][0]['rows']), 4)
        self.assertTrue(int(content['data'][0]['bytes_on_disk']) == pytest.approx(704, 50))

    @tornado.testing.gen_test
    async def test_track_usage_metrics_storage_counts_quarantine_rows_v2(self):
        usage_metrics_tracker = UsageMetricsTracker()
        public_user = public.get_public_user()
        usage_metrics_storage = public_user.get_datasource('usage_metrics_storage__v2')

        workspace_name = f"test_track_usage_quarantine_{uuid.uuid4().hex}"
        email = f'{workspace_name}@example.com'
        workspace = await self.tb_api_proxy_async.register_user_and_workspace(email, workspace_name)
        token = Users.get_token_for_scope(workspace, scopes.ADMIN)
        self.workspaces_to_delete.append(workspace)

        await self.tb_api_proxy_async.create_datasource_from_data(
            token=token,
            ds_name='datasource_a',
            data=StringIO("d,sales\n2019-01-01,2\n2019-01-02,3")
        )
        ds_a = Users.get_datasource(workspace, 'datasource_a')

        await self.tb_api_proxy_async.create_datasource_from_data(
            token=token,
            ds_name='datasource_a',
            data=StringIO("d,sales\nwrong_date,2\nwrong_date,3"),
            extra_params={'mode': 'append'}
        )

        ds_a = Users.get_datasource(workspace, 'datasource_a')

        self.wait_for_datasource_replication(workspace, ds_a, quarantine=True)

        usage_metrics_tracker.track_usage_metrics_storage(
            public_user,
            [User.get_by_id(workspace.id)]
        )

        self.wait_for_public_table_replication(usage_metrics_storage.name)
        content = exec_sql(public_user.database, f"select * from {usage_metrics_storage.id} FINAL WHERE user_id='{workspace.id}' FORMAT JSON")

        self.assertEqual(len(content['data']), 1)

        for row in content['data']:
            self.assertEqual(row['datasource_id'], ds_a.id)
            self.assertTrue(row['timestamp'])
            self.assertTrue(row['user_id'] == workspace.id)
            self.assertEqual(int(row['rows']), 2)
            self.assertEqual(int(row['bytes']), pytest.approx(155, 25))
            self.assertEqual(int(row['rows_quarantine']), 2)
            self.assertEqual(int(row['bytes_quarantine']), pytest.approx(155, 25))

    @tornado.testing.gen_test
    @pytest.mark.skip(
        "usage_metrics_storage is going to be deprecated with https://gitlab.com/tinybird/analytics/-/issues/5280.")
    async def test_track_usage_metrics_storage_filters_temporary_datasources(self):
        usage_metrics_tracker = UsageMetricsTracker()
        public_user = public.get_public_user()
        usage_metrics_storage = public_user.get_datasource('usage_metrics_storage')

        workspace_name = f"test_track_usage_quarantine_{uuid.uuid4().hex}"
        email = f'{workspace_name}@example.com'
        workspace = await self.tb_api_proxy_async.register_user_and_workspace(email, workspace_name)
        token = Users.get_token_for_scope(workspace, scopes.ADMIN)
        self.workspaces_to_delete.append(workspace)

        response = await self.tb_api_proxy_async.create_datasource_from_data(
            token=token,
            ds_name='datasource_a',
            data=StringIO("d,sales\n2019-01-01,2\n2019-01-02,3")
        )

        datasource_a = response['datasource']
        await ch_create_table_as_table(
            database_server=workspace.database_server,
            database=workspace.database,
            table_name='t_1234_tmp_1234',
            as_table_name=datasource_a['id'],
            storage_policy=workspace.storage_policy,
            engine='Null()',
            cluster='tinybird',
            as_table_database=workspace.database)
        exec_sql(workspace.database, f"INSERT INTO {workspace.database}.t_1234_tmp_1234 VALUES ('2019-01-01',4)")
        await ch_create_table_as_table(
            database_server=workspace.database_server,
            database=workspace.database,
            table_name='t_1234_mirror',
            as_table_name=datasource_a['id'],
            storage_policy=workspace.storage_policy,
            engine='Null()',
            cluster='tinybird',
            as_table_database=workspace.database)
        exec_sql(workspace.database, f"INSERT INTO {workspace.database}.t_1234_mirror VALUES ('2019-01-01',4)")

        usage_metrics_tracker.track_usage_metrics_storage(
            public_user,
            [User.get_by_id(workspace.id)]
        )

        self.wait_for_public_table_replication(usage_metrics_storage.name)
        content = exec_sql(public_user.database, f"select * from {usage_metrics_storage.id} FINAL WHERE database='{workspace.database}' FORMAT JSON")

        self.assertTrue(content['data'][0]['date'])
        self.assertTrue(content['data'][0]['database'] == workspace.database)
        self.assertTrue(int(content['data'][0]['rows']) == 2)
        self.assertTrue(int(content['data'][0]['bytes_on_disk']) == pytest.approx(159, 50))

    @tornado.testing.gen_test
    @patch.object(UsageMetricsTracker, '_retrieve_storage_used_per_database_and_table')
    async def test_track_usage_metrics_storage_no_cluster_assigned_not_found(self, mock_retrieve):
        usage_metrics_tracker = UsageMetricsTracker()
        public_user = public.get_public_user()
        usage_metrics_storage = public_user.get_datasource('usage_metrics_storage__v2')

        workspace_name = f"test_track_usage_quarantine_{uuid.uuid4().hex}"
        email = f'{workspace_name}@example.com'
        workspace = await self.tb_api_proxy_async.register_user_and_workspace(email, workspace_name)
        token = Users.get_token_for_scope(workspace, scopes.ADMIN)
        self.workspaces_to_delete.append(workspace)

        await self.tb_api_proxy_async.create_datasource_from_data(
            token=token,
            ds_name='datasource_a',
            data=StringIO("d,sales\n2019-01-01,2\n2019-01-02,3")
        )
        ds_a = Users.get_datasource(workspace, 'datasource_a')

        self.wait_for_datasource_replication(workspace, ds_a)

        mock_retrieve.return_value = {'cluster1': {'other_db': {'other_ds': {'rows': 1, 'bytes_on_disk': 10},
                                                                "other_ds_quarantine": {'rows': 2, 'bytes_on_disk': 20}}}}

        usage_metrics_tracker.track_usage_metrics_storage(
            public_user,
            [User.get_by_id(workspace.id)]
        )
        self.wait_for_public_table_replication(usage_metrics_storage.name)
        content = exec_sql(public_user.database, f"select * from {usage_metrics_storage.id} FINAL WHERE user_id='{workspace.id}' FORMAT JSON")
        self.assertEqual(len(content['data']), 0)
