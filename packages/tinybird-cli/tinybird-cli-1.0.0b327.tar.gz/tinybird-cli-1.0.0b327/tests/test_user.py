import pickle
import unittest
import tornado
import uuid

from unittest.mock import patch
from datetime import date, timedelta

from tornado.testing import AsyncTestCase
from chtoolset import query as chquery
from freezegun import freeze_time

from tinybird.constants import CHCluster
from tinybird.token_scope import scopes
from tinybird.user import UserAccount, UserDoesNotExist, Users, User, PipeWithoutEndpoint, QueryNotAllowed, public, DatabaseNameCollisionError
from tinybird.redis_client import get_redis_test_client
from tinybird.plans import BillingPlans
from tinybird.default_tables import Replacement, c, FeaturedColumns

from .conftest import CH_ADDRESS
from .views.base_test import BaseTest, TBApiProxyAsync


class TestUserModelWithRedisMaster(BaseTest):

    def setUp(self):
        USER = f'test_redis_{uuid.uuid4().hex}@example.com'
        WORKSPACE = f'test_workspace_redis_{uuid.uuid4().hex}'

        self.redis_client = get_redis_test_client()
        self.user_account = UserAccount.register(USER, 'pass')
        self.user = User.register(WORKSPACE, self.user_account.id)
        super().setUp()

    def tearDown(self):
        User._delete(self.user.id)
        UserAccount._delete(self.user_account.id)
        super().tearDown()

    def _get_from_redis(self, uid):
        f = self.redis_client.get('users:' + uid)
        return pickle.loads(f)

    def test_user_should_be_in_redis(self):
        u = self._get_from_redis(self.user['id'])
        self.assertEqual(u['id'], self.user['id'])

        u = Users.get_by_id(self.user['id'])
        self.assertEqual(u['id'], self.user['id'])

    def test_user_by_name(self):
        u = Users.get_by_name(self.user['name'])
        self.assertEqual(u['id'], self.user['id'])

    def test_user_by_database(self):
        u = Users.get_by_database(self.user['database'])
        self.assertEqual(u['id'], self.user['id'])

    def test_non_existing_user(self):
        with self.assertRaises(UserDoesNotExist):
            Users.get_by_id('asdasd')
        # self.assertEqual(u['id'], self.user['id'])

    def test_should_update(self):
        # change
        Users.add_datasource(self.user, 'testing')
        # read
        u = Users.get_by_id(self.user['id'])
        ds = Users.get_datasources(u)
        self.assertEqual(len(ds), 1)


class TestUserReplaceTablesTemplateSetting(BaseTest):

    scenarios = [
        (
            'limit_threads',
            [
                {
                    'name': 'endpoint',
                    'sql': "% {{ max_threads(3) }} select 1 as a"
                }
            ],
            3
        ),
        (
            'limit_threads_other_node',
            [
                {
                    'name': 'first_node',
                    'sql': "% {{ max_threads(17) }} select 1 as a"
                },
                {
                    'name': 'endpoint',
                    'sql': "SELECT * FROM first_node"
                }
            ],
            17
        )
    ]

    def _prepare_test(self, pipe_name, nodes):
        u = Users.get_by_id(self.WORKSPACE_ID)

        token_name = f'{pipe_name} endpoint api'
        with User.transaction(u.id) as user:
            pipe = user.add_pipe(pipe_name, nodes=nodes)
            endpoint_node = next((n for n in pipe.pipeline.nodes if n.name == 'endpoint'), None) or pipe.pipeline.nodes[-1]
            pipe.endpoint = endpoint_node.id
            user.update_pipe(pipe)
            user.add_token(token_name, scopes.PIPES_READ, pipe.id)

        u = Users.get_by_id(self.WORKSPACE_ID)
        pipe = u.get_pipe(pipe_name)
        access_info = u.get_token_access_info(token_name)
        readable_resources = access_info.get_resources_for_scope(scopes.DATASOURCES_READ, scopes.PIPES_READ)
        return u, pipe, readable_resources

    def test_template_max_threads_setting(self):
        for pipe_name, nodes, expected_max_threads in self.scenarios:
            with self.subTest(pipe_name=pipe_name):
                u, pipe, readable_resources = self._prepare_test(pipe_name, nodes)

                template_execution_results = {}
                _ = u.replace_tables(f'SELECT * FROM {pipe_name}',
                                     readable_resources=readable_resources,
                                     pipe=pipe,
                                     template_execution_results=template_execution_results)

                self.assertEqual(template_execution_results.get('max_threads', None), expected_max_threads)

    @tornado.testing.gen_test
    async def test_template_max_threads_setting_executor(self):
        for pipe_name, nodes, expected_max_threads in self.scenarios:
            with self.subTest(pipe_name=pipe_name):
                u, pipe, readable_resources = self._prepare_test(pipe_name, nodes)

                template_execution_results = {}
                _ = await u.replace_tables_async(f'SELECT * FROM {pipe_name}',
                                                 readable_resources=readable_resources,
                                                 pipe=pipe,
                                                 template_execution_results=template_execution_results)

                self.assertEqual(template_execution_results.get('max_threads', None), expected_max_threads)


class TestUserReplaceTablesTemplateBackendHintSetting(BaseTest):

    scenarios = [
        (
            'backend_hint',
            [
                {
                    'name': 'endpoint',
                    'sql': "% {{ backend_hint('foo') }} select 1 as a"
                }
            ],
            'foo'
        ),
        (
            'backend_hint_non_str',
            [
                {
                    'name': 'endpoint',
                    'sql': "% {{ backend_hint(0) }} select 1 as a"
                }
            ],
            '0'
        ),
        (
            'backend_hint_other_node',
            [
                {
                    'name': 'first_node',
                    'sql': "% {{ backend_hint('bar') }} select 1 as a"
                },
                {
                    'name': 'endpoint',
                    'sql': "SELECT * FROM first_node"
                }
            ],
            'bar'
        ),
        (
            'backend_hint_disabled_none',
            [
                {
                    'name': 'endpoint',
                    'sql': "% {{ backend_hint(None) }} select 1 as a"
                }
            ],
            None
        ),
        (
            'backend_hint_disabled_false',
            [
                {
                    'name': 'endpoint',
                    'sql': "% {{ backend_hint(False) }} select 1 as a"
                }
            ],
            None
        ),
    ]

    def _prepare_test(self, pipe_name, nodes):
        u = Users.get_by_id(self.WORKSPACE_ID)

        token_name = f'{pipe_name} endpoint api'
        with User.transaction(u.id) as user:
            pipe = user.add_pipe(pipe_name, nodes=nodes)
            endpoint_node = next((n for n in pipe.pipeline.nodes if n.name == 'endpoint'), None) or pipe.pipeline.nodes[-1]
            pipe.endpoint = endpoint_node.id
            user.update_pipe(pipe)
            user.add_token(token_name, scopes.PIPES_READ, pipe.id)

        u = Users.get_by_id(self.WORKSPACE_ID)
        pipe = u.get_pipe(pipe_name)
        access_info = u.get_token_access_info(token_name)
        readable_resources = access_info.get_resources_for_scope(scopes.DATASOURCES_READ, scopes.PIPES_READ)
        return u, pipe, readable_resources

    def test_template_backend_hint_setting(self):
        for pipe_name, nodes, expected_backend_hint in self.scenarios:
            with self.subTest(pipe_name=pipe_name):
                u, pipe, readable_resources = self._prepare_test(pipe_name, nodes)

                template_execution_results = {}
                _ = u.replace_tables(f'SELECT * FROM {pipe_name}',
                                     readable_resources=readable_resources,
                                     pipe=pipe,
                                     template_execution_results=template_execution_results)

                self.assertEqual(template_execution_results.get('backend_hint', 'whatever'), expected_backend_hint)

    @tornado.testing.gen_test
    async def test_template_backend_hint_setting_executor(self):
        for pipe_name, nodes, expected_backend_hint in self.scenarios:
            with self.subTest(pipe_name=pipe_name):
                u, pipe, readable_resources = self._prepare_test(pipe_name, nodes)

                template_execution_results = {}
                _ = await u.replace_tables_async(f'SELECT * FROM {pipe_name}',
                                                 readable_resources=readable_resources,
                                                 pipe=pipe,
                                                 template_execution_results=template_execution_results)

                self.assertEqual(template_execution_results.get('backend_hint', 'whatever'), expected_backend_hint)


class TestUserReplaceTablesBasic(BaseTest):

    def setUp(self):
        super(TestUserReplaceTablesBasic, self).setUp()
        self.tb_api_proxy_async = TBApiProxyAsync(self)

    def test_migrated(self):
        user_name = f'test_replace_tables_{uuid.uuid4().hex}'
        user_account = UserAccount.register(f'{user_name}@example.com', 'pass')
        u = User.register(user_name, user_account.id)

        ds = Users.add_datasource(u, 'foo')

        sql_from_name = Users.replace_tables(u, "select * from foo")
        sql_from_db_id = chquery.format(Users.replace_tables(u, f"select * from {u['database']}.{ds.id} AS foo"))
        self.assertEqual(sql_from_name, sql_from_db_id)

        pipe = Users.add_pipe(u, 'test_pipe', 'select * from foo')
        with self.assertRaisesRegex(PipeWithoutEndpoint, r'does not have an endpoint yet'):
            Users.replace_tables(u, f"select * from {pipe.name}")

        pipe.endpoint = pipe.pipeline.nodes[0].id
        Users.update_pipe(u, pipe)

        expected_query_with_name = chquery.format(f"select * from (SELECT * FROM {u['database']}.{ds.id} AS foo) as {pipe.name}")
        expected_query_with_id = chquery.format(f"select * from (SELECT * FROM {u['database']}.{ds.id} AS foo) as {pipe.id}")
        self.assertEqual(Users.replace_tables(u, f"select * from {pipe.name}"), expected_query_with_name)
        self.assertEqual(Users.replace_tables(u, f"select * from {pipe.id}"), expected_query_with_id)

        with self.assertRaisesRegex(QueryNotAllowed, rf"Resource '{pipe.endpoint}' not found"):
            Users.replace_tables(u, f"select * from {pipe.endpoint}")

        self.assertEqual(Users.replace_tables(u, f"select * from {pipe.id}", pipe=pipe), expected_query_with_id)

        with self.assertRaisesRegex(QueryNotAllowed, r"Resource 'system.block_log' not found"):
            Users.replace_tables(u, "select * from system.block_log")

        with self.assertRaisesRegex(QueryNotAllowed, r"Resource 'block_log' not found"):
            Users.replace_tables(u, "select * from block_log")

        q = Users.replace_tables(u, "select * from tinybird.block_log")
        self.assertIsNotNone(q)

    @tornado.testing.gen_test
    async def test_shared_internal_ds(self):
        ws_public = public.get_public_user()
        public_user_account = UserAccount.get_by_email(public.get_public_email())
        user_name = f'test_replace_shared_internal_tables_{uuid.uuid4().hex}'
        user_account = UserAccount.register(f'{user_name}@example.com', 'pass')
        workspace = User.register(user_name, user_account.id, CHCluster('tinybird', User.default_database_server))
        token_user_account = UserAccount.get_token_for_scope(user_account, scopes.AUTH)

        # before sharing replacements include filters (i.e billable)
        q = Users.replace_tables(workspace, "select * from tinybird.pipe_stats")

        self.assertIn('AND (billable = 1)', q)
        token = UserAccount.get_token_for_scope(public_user_account, scopes.AUTH)
        await self.tb_api_proxy_async.invite_user_to_workspace(
            token=token,
            workspace_id=ws_public.id,
            user_to_invite_email=user_account.email
        )
        await self.tb_api_proxy_async.make_user_workspace_admin(token=token, workspace_id=ws_public.id, user_email=user_account.email)
        await self.tb_api_proxy_async.share_datasource_with_another_workspace(
            token=token_user_account,
            datasource_id=ws_public.get_datasource('pipe_stats').id,
            origin_workspace_id=ws_public.id,
            destination_workspace_id=workspace.id,
            expect_notification=False
        )

        workspace = User.get_by_id(workspace.id)
        self.assertEqual(len(workspace.get_datasources()), 1)
        self.assertEqual(workspace.get_datasources()[0].original_ds_name, 'pipe_stats')

        # after sharing replacements doesn't include filters (i.e billable)
        q = Users.replace_tables(workspace, "select * from tinybird.pipe_stats")
        self.assertNotIn('AND (billable = 1)', q)

    @tornado.testing.gen_test
    async def test_feature_columns_replacements(self):
        # TODO: make this test less data dependant
        user_name = f'test_replace_feature_columns_tables_{uuid.uuid4().hex}'
        user_account = UserAccount.register(f'{user_name}@example.com', 'pass')
        workspace = User.register(user_name, user_account.id, CHCluster('tinybird', User.default_database_server))

        mock_replacements = [Replacement(
            namespace='tinybird',
            name='datasources_ops_log',
            resource='datasources_ops_log',
            columns=c('timestamp', 'event_type', 'datasource_id', 'datasource_name', 'result', 'elapsed_time',
                      'error', 'Options.Names', 'Options.Values', 'request_id', 'import_id', 'job_id', 'rows',
                      'rows_quarantine', 'blocks_ids'),
            filter_by_user=True,
            include_read_only_datasources=True,
            featured_columns=FeaturedColumns(feature_flag="ANY_FEATURED_FLAG",
                                             columns=c('timestamp', 'event_type', 'datasource_id', 'datasource_name',
                                                       'result', 'elapsed_time',
                                                       'error', 'Options.Names', 'Options.Values', 'request_id',
                                                       'import_id', 'job_id', 'rows', 'rows_quarantine', 'blocks_ids',
                                                       'operation_id', 'read_rows', 'read_bytes', 'written_rows',
                                                       'written_bytes', 'written_rows_quarantine',
                                                       'written_bytes_quarantine',
                                                       'pipe_id', 'pipe_name')),
        )]

        with patch('tinybird.user.REPLACEMENTS', mock_replacements):
            with patch('tinybird.user.FeatureFlagsWorkspaceService.feature_for_id', return_value=False):
                q = Users.replace_tables(workspace, "select * from tinybird.datasources_ops_log")
                self.assertNotIn('operation_id', q)

        with patch('tinybird.user.REPLACEMENTS', mock_replacements):
            with patch('tinybird.user.FeatureFlagsWorkspaceService.feature_for_id', return_value=True):
                q = Users.replace_tables(workspace, "select * from tinybird.datasources_ops_log")
                self.assertIn('operation_id', q)

    @tornado.testing.gen_test
    async def test_replace_filtering_by_database(self):
        user_name = f'test_replace_filter_by_database_{uuid.uuid4().hex}'
        user_account = UserAccount.register(f'{user_name}@example.com', 'pass')
        workspace = User.register(user_name, user_account.id, CHCluster('tinybird', User.default_database_server))
        q = Users.replace_tables(workspace, "select * from tinybird.bi_stats_rt")
        self.assertIn(f"WHERE database = '{workspace.database}'", q)


class TestUserSetNameFromNotNormalizedEmail(unittest.TestCase):

    @staticmethod
    def _user_workspace_tear_down(email, name):
        try:
            u = UserAccount.get_by_email(email)
            UserAccount._delete(u.id)
        except Exception:
            pass

        try:
            u = User.get_by_name(name)
            User._delete(u.id)
        except Exception:
            pass

    def test_happy_path(self):
        name = f'test.email_{uuid.uuid4().hex}'
        name_replaced = name.replace('.', '_')
        email = f'{name}@example.com'
        self._user_workspace_tear_down(email, name_replaced)

        user_account = UserAccount.register(email, 'pass')
        workspace = User.register(name=name, normalize_name_and_try_different_on_collision=True, admin=user_account.id)

        refresed_workspace = User.get_by_id(workspace.id)
        self.assertEqual(refresed_workspace.name, name_replaced)

    @patch('tinybird.user.User._get_string_with_random_numbers', side_effect=lambda value: '9' * value)
    def test_case_where_the_normalized_email_is_already_taken(self, _get_string_with_random_numbers_mock):
        first_name = f'test.email_{uuid.uuid4().hex}'
        email = f'{first_name}@example.com'
        second_name = first_name

        self._user_workspace_tear_down(email, first_name)

        user_account = UserAccount.register(email, 'pass')
        first_workspace = User.register(name=first_name, normalize_name_and_try_different_on_collision=True, admin=user_account.id)
        second_workspace = User.register(name=second_name, normalize_name_and_try_different_on_collision=True, admin=user_account.id)

        refresed_first_workspace = User.get_by_id(first_workspace.id)
        self.assertEqual(refresed_first_workspace.name, first_name.replace('.', '_'))

        refresed_second_workspace = User.get_by_id(second_workspace.id)
        self.assertEqual(refresed_second_workspace.name, f'{first_name}_99'.replace('.', '_'))


class TestWorkspaceDatabaseColission(unittest.TestCase):

    def test_create_database_collision(self):
        with patch('tinybird.user.User.get_by_database', return_value=None):
            with self.assertRaises(DatabaseNameCollisionError):
                User.generate_uid_and_database_name_and_try_different_on_collision()


class TestWorkspaceDelete(unittest.TestCase):
    def setUp(self):
        self.email = f'test_workspace_deletion_{uuid.uuid4().hex}@example.com'
        self.workspace_name = f'test_workspace_deletion_{uuid.uuid4().hex}'

        self.redis_client = get_redis_test_client()
        self.user_account = UserAccount.register(self.email, 'pass')
        self.workspace = User.register(self.workspace_name, self.user_account.id)

    def tearDown(self):
        User._delete(self.workspace.id)
        UserAccount._delete(self.user_account.id)

    def test_delete_happy_path(self):
        Users.delete(self.workspace)
        refreshed_workspace = User.get_by_id(self.workspace.id)

        self.assertTrue(refreshed_workspace.deleted)
        self.assertFalse(refreshed_workspace.confirmed_account)
        self.assertIn('deleted', refreshed_workspace.name)

    def test_once_a_ws_is_deleted_its_name_can_be_reused(self):
        name_before_deletion = self.workspace.name
        Users.delete(self.workspace)
        refreshed_workspace = User.get_by_id(self.workspace.id)
        self.assertIn('deleted', refreshed_workspace.name)

        the_new_workspace_created = User.register(name_before_deletion, self.user_account.id)
        self.assertIsNotNone(the_new_workspace_created)


class TestUserGetClusters(AsyncTestCase):

    def setUp(self):
        super(TestUserGetClusters, self).setUp()

        self.workspaces_to_delete = []
        self.users_to_delete = []

        self.main_clickhouse_url = CH_ADDRESS

    def tearDown(self):
        for ws in reversed(self.workspaces_to_delete):
            User._delete(ws.id)
        for ua in self.users_to_delete:
            UserAccount._delete(ua.id)
        super(TestUserGetClusters, self).tearDown()

    @tornado.testing.gen_test
    async def test_get_cluster_returns_default_for_non_configured_emails(self):
        user = UserAccount.register(f'test{uuid.uuid4().hex}@developeruser.co')
        self.users_to_delete.append(user)

        returned_cluster = await user.get_cluster()

        self.assertEqual(CHCluster(name=User.default_cluster, server_url=User.default_database_server), returned_cluster)

    @tornado.testing.gen_test
    @patch('tinybird.user.OrganizationEmailsCluster', {'developeruser.co': [CHCluster('tinybird', '127.0.0.1')]})
    async def test_get_cluster_returns_configuration_for_email(self):
        user = UserAccount.register(f'test{uuid.uuid4().hex}@developeruser.co')
        self.users_to_delete.append(user)

        returned_cluster = await user.get_cluster()
        self.assertEqual('127.0.0.1', returned_cluster.server_url)
        self.assertEqual('tinybird', returned_cluster.name)

    @tornado.testing.gen_test
    @patch('tinybird.user.OrganizationEmailsCluster', {'developeruser.co': [CHCluster('non_existing_cluster', '127.0.0.1')]})
    async def test_get_cluster_raises_error_if_configured_cluster_doesnt_exists(self):
        user = UserAccount.register(f'test{uuid.uuid4().hex}@developeruser.co')
        self.users_to_delete.append(user)

        try:
            _ = await user.get_cluster()
            self.assertTrue(False, 'You should not be reading this')
        except Exception as ex:
            expected: str = "Workspace creation error: your organization doesn't have clusters in this region, try a different region"
            self.assertIn(expected, str(ex))

    @tornado.testing.gen_test
    @patch('tinybird.user.OrganizationEmailsCluster', {'developeruser.co': [CHCluster('tinybird', '127.0.0.1')]})
    async def test_get_cluster_does_not_return_cluster_used_in_the_first_workspace_created_by_the_user_when_email_config_is_present(self):
        user = UserAccount.register(f'test{uuid.uuid4().hex}@developeruser.co')
        self.users_to_delete.append(user)

        new_workspace_1 = User.register(name=f"test{uuid.uuid4().hex}", admin=user.id)
        self.workspaces_to_delete.append(new_workspace_1)
        new_workspace_2 = User.register(name=f"test{uuid.uuid4().hex}", admin=user.id)

        self.workspaces_to_delete.append(new_workspace_2)

        with User.transaction(new_workspace_1.id) as w:
            w.clusters = ['cluster_from_oldest_ws']
            w.database_server = '1.1.1.1'

        with User.transaction(new_workspace_2.id) as w:
            w.clusters = ['cluster_from_newest_ws']
            w.database_server = '1.1.1.2'

        returned_cluster = await user.get_cluster()
        self.assertEqual('127.0.0.1', returned_cluster.server_url)
        self.assertEqual('tinybird', returned_cluster.name)

    @tornado.testing.gen_test
    async def test_get_cluster_return_cluster_used_in_the_first_workspace_created_by_the_user_when_email_config_is_not_present(self):
        user = UserAccount.register(f'test{uuid.uuid4().hex}@developeruser.co')
        self.users_to_delete.append(user)

        new_workspace_1 = User.register(name=f"test{uuid.uuid4().hex}", admin=user.id)
        self.workspaces_to_delete.append(new_workspace_1)
        new_workspace_2 = User.register(name=f"test{uuid.uuid4().hex}", admin=user.id)

        self.workspaces_to_delete.append(new_workspace_2)

        with User.transaction(new_workspace_1.id) as w:
            w.clusters = ['cluster_from_oldest_ws']
            w.database_server = '1.1.1.1'

        with User.transaction(new_workspace_2.id) as w:
            w.clusters = ['cluster_from_newest_ws']
            w.database_server = '1.1.1.2'

        returned_cluster = await user.get_cluster()
        self.assertEqual('1.1.1.1', returned_cluster.server_url)
        self.assertEqual('cluster_from_oldest_ws', returned_cluster.name)


class TestNotifyBuildPlanLimits(AsyncTestCase):

    def setUp(self):
        super(TestNotifyBuildPlanLimits, self).setUp()
        self.workspaces_to_delete = []
        self.users_to_delete = []
        user_account = UserAccount.register(f"test_notify_build_plan{uuid.uuid4().hex}@example.com", 'pass')
        self.users_to_delete.append(user_account)
        self.first_workspace = User.register(
            name=f"test_workspace_notify_build_plan_{uuid.uuid4().hex}",
            admin=user_account.id)
        self.workspaces_to_delete.append(self.first_workspace)

    def tearDown(self):
        for ws in reversed(self.workspaces_to_delete):
            User._delete(ws.id)
        for ua in self.users_to_delete:
            UserAccount._delete(ua.id)
        super(TestNotifyBuildPlanLimits, self).tearDown()

    @tornado.testing.gen_test
    @freeze_time('2022-03-30')
    @patch('tinybird.user.Users._send_notification_on_build_plan_limits')
    async def test_notify_build_plan_limits_just_upgraded(self, mock_send_notification):
        self.first_workspace.plan = BillingPlans.PRO
        self.first_workspace.save()
        await Users.notify_build_plan_limits(self.first_workspace.id, 1000, 10, 0.07, 0.34, False, 800, 7)
        mock_send_notification.assert_not_called()
        self.first_workspace = Users.get_by_id(self.first_workspace.id)
        self.assertIsNone(self.first_workspace.billing_details.get('notifications'))

    @tornado.testing.gen_test
    @freeze_time('2022-03-30')
    @patch('tinybird.user.Users._send_notification_on_build_plan_limits')
    async def test_notify_build_plan_limits_reaching_empty_notifications(self, mock_send_notification):
        await Users.notify_build_plan_limits(self.first_workspace.id, 1000, 10, 0.07, 0.34, False, 800, 7)
        mock_send_notification.assert_called_once_with(self.first_workspace, 1000, 10, 0.07, 0.34,
                                                       False, 800, 7)
        self.first_workspace = Users.get_by_id(self.first_workspace.id)
        self.assertEqual(self.first_workspace.billing_details['notifications'], {'plan_reaching': date.today()})

    @tornado.testing.gen_test
    @freeze_time('2022-03-30')
    @patch('tinybird.user.Users._send_notification_on_build_plan_limits')
    async def test_notify_build_plan_limits_reaching_already_reaching_sent(self, mock_send_notification):
        self.first_workspace.billing_details = {'notifications': {'plan_reaching': date.today()}}
        self.first_workspace.save()
        await Users.notify_build_plan_limits(self.first_workspace.id, 1000, 10, 0.07, 0.34, False, 800, 7)
        mock_send_notification.assert_not_called()
        self.first_workspace = Users.get_by_id(self.first_workspace.id)
        self.assertEqual(self.first_workspace.billing_details['notifications'], {'plan_reaching': date.today()})

    @tornado.testing.gen_test
    @patch('tinybird.user.Users._send_notification_on_build_plan_limits')
    async def test_notify_build_plan_limits_reaching_already_reaching_sent_yesterday(self, mock_send_notification):
        self.first_workspace.billing_details = {'notifications': {'plan_reaching': date.today() - timedelta(days=1)}}
        self.first_workspace.save()
        await Users.notify_build_plan_limits(self.first_workspace.id, 1000, 10, 0.07, 0.34, False, 800, 7)
        mock_send_notification.assert_called_once_with(self.first_workspace, 1000, 10, 0.07, 0.34,
                                                       False, 800, 7)
        self.first_workspace = Users.get_by_id(self.first_workspace.id)
        self.assertEqual(self.first_workspace.billing_details['notifications'], {'plan_reaching': date.today()})

    @tornado.testing.gen_test
    @freeze_time('2022-03-30')
    @patch('tinybird.user.Users._send_notification_on_build_plan_limits')
    async def test_notify_build_plan_limits_reaching_already_reaching_sent_yesterday_only_requests(self, mock_send_notification):
        self.first_workspace.billing_details = {'notifications': {'plan_reaching': date.today() - timedelta(days=1)}}
        self.first_workspace.save()
        await Users.notify_build_plan_limits(self.first_workspace.id, 1000, 10, 0.07, 0.34, False, 800, None)
        mock_send_notification.assert_called_once_with(self.first_workspace, 1000, 10, 0.07, 0.34,
                                                       False, 800, None)
        self.first_workspace = Users.get_by_id(self.first_workspace.id)
        self.assertEqual(self.first_workspace.billing_details['notifications'], {'plan_reaching': date.today()})

    @tornado.testing.gen_test
    @freeze_time('2022-03-30')
    @patch('tinybird.user.Users._send_notification_on_build_plan_limits')
    async def test_notify_build_plan_limits_reaching_already_reaching_sent_yesterday_only_storage(self, mock_send_notification):
        self.first_workspace.billing_details = {'notifications': {'plan_reaching': date.today() - timedelta(days=1)}}
        self.first_workspace.save()
        await Users.notify_build_plan_limits(self.first_workspace.id, 1000, 10, 0.07, 0.34, False, None, 7)
        mock_send_notification.assert_not_called()
        self.first_workspace = Users.get_by_id(self.first_workspace.id)
        self.assertEqual(self.first_workspace.billing_details['notifications'], {'plan_reaching': date.today() - timedelta(days=1)})

    @tornado.testing.gen_test
    @freeze_time('2022-03-30')
    @patch('tinybird.user.Users._send_notification_on_build_plan_limits')
    async def test_notify_build_plan_limits_reaching_already_reaching_sent_prev_month_only_storage(self, mock_send_notification):
        self.first_workspace.billing_details = {'notifications': {'plan_reaching': date.today() - timedelta(days=40)}}
        self.first_workspace.save()
        await Users.notify_build_plan_limits(self.first_workspace.id, 1000, 10, 0.07, 0.34, False, None, 7)
        mock_send_notification.assert_called_once_with(self.first_workspace, 1000, 10, 0.07, 0.34,
                                                       False, None, 7)
        self.first_workspace = Users.get_by_id(self.first_workspace.id)
        self.assertEqual(self.first_workspace.billing_details['notifications'], {'plan_reaching': date.today()})

    @tornado.testing.gen_test
    @freeze_time('2022-03-30')
    @patch('tinybird.user.Users._send_notification_on_build_plan_limits')
    async def test_notify_build_plan_limits_exceeded_already_reaching_sent(self, mock_send_notification):
        self.first_workspace.billing_details = {'notifications': {'plan_reaching': date.today()}}
        self.first_workspace.save()
        await Users.notify_build_plan_limits(self.first_workspace.id, 1000, 10, 0.07, 0.34, True, 800, 7)
        mock_send_notification.assert_called_once_with(self.first_workspace, 1000, 10, 0.07, 0.34,
                                                       True, 800, 7)
        self.first_workspace = Users.get_by_id(self.first_workspace.id)
        self.assertEqual(self.first_workspace.billing_details['notifications'], {'plan_reaching': date.today(),
                                                                                 'plan_exceeded': date.today()})

    @tornado.testing.gen_test
    @freeze_time('2022-03-30')
    @patch('tinybird.user.Users._send_notification_on_build_plan_limits')
    async def test_notify_build_plan_limits_exceeded_already_exceeded_sent(self, mock_send_notification):
        self.first_workspace.billing_details = {'notifications': {'plan_reaching': date.today(),
                                                                  'plan_exceeded': date.today()}
                                                }
        self.first_workspace.save()
        await Users.notify_build_plan_limits(self.first_workspace.id, 1000, 10, 0.07, 0.34, True, 800, 7)
        mock_send_notification.assert_not_called()
        self.first_workspace = Users.get_by_id(self.first_workspace.id)
        self.assertEqual(self.first_workspace.billing_details['notifications'], {'plan_reaching': date.today(),
                                                                                 'plan_exceeded': date.today()})

    @tornado.testing.gen_test
    @freeze_time('2022-03-30')
    @patch('tinybird.user.Users._send_notification_on_build_plan_limits')
    async def test_notify_build_plan_limits_exceeded_already_exceeded_sent_yesterday(self, mock_send_notification):
        self.first_workspace.billing_details = {'notifications': {'plan_reaching': date.today() - timedelta(days=1),
                                                                  'plan_exceeded': date.today() - timedelta(days=1)}
                                                }
        self.first_workspace.save()
        await Users.notify_build_plan_limits(self.first_workspace.id, 1000, 10, 0.07, 0.34, True, 800, 7)
        mock_send_notification.assert_called_once_with(self.first_workspace, 1000, 10, 0.07, 0.34,
                                                       True, 800, 7)
        self.first_workspace = Users.get_by_id(self.first_workspace.id)
        self.assertEqual(self.first_workspace.billing_details['notifications'], {'plan_reaching': date.today() - timedelta(days=1),
                                                                                 'plan_exceeded': date.today()})

    @tornado.testing.gen_test
    @freeze_time('2022-03-30')
    @patch('tinybird.user.Users._send_notification_on_build_plan_limits')
    async def test_notify_build_plan_limits_exceeded_already_exceeded_sent_yesterday_only_requests(self, mock_send_notification):
        self.first_workspace.billing_details = {'notifications': {'plan_reaching': date.today() - timedelta(days=1),
                                                                  'plan_exceeded': date.today() - timedelta(days=1)}
                                                }
        self.first_workspace.save()
        await Users.notify_build_plan_limits(self.first_workspace.id, 1000, 10, 0.07, 0.34, True, 800, None)
        mock_send_notification.assert_called_once_with(self.first_workspace, 1000, 10, 0.07, 0.34,
                                                       True, 800, None)
        self.first_workspace = Users.get_by_id(self.first_workspace.id)
        self.assertEqual(self.first_workspace.billing_details['notifications'], {'plan_reaching': date.today() - timedelta(days=1),
                                                                                 'plan_exceeded': date.today()})

    @tornado.testing.gen_test
    @freeze_time('2022-03-30')
    @patch('tinybird.user.Users._send_notification_on_build_plan_limits')
    async def test_notify_build_plan_limits_exceeded_already_exceeded_sent_yesterday_only_storage(self, mock_send_notification):
        self.first_workspace.billing_details = {'notifications': {'plan_reaching': date.today() - timedelta(days=1),
                                                                  'plan_exceeded': date.today() - timedelta(days=1)}
                                                }
        self.first_workspace.save()
        await Users.notify_build_plan_limits(self.first_workspace.id, 1000, 10, 0.07, 0.34, True, None, 11)
        mock_send_notification.assert_not_called()
        self.first_workspace = Users.get_by_id(self.first_workspace.id)
        self.assertEqual(self.first_workspace.billing_details['notifications'], {'plan_reaching': date.today() - timedelta(days=1),
                                                                                 'plan_exceeded': date.today() - timedelta(days=1)})

    @tornado.testing.gen_test
    @freeze_time('2022-03-30')
    @patch('tinybird.user.Users._send_notification_on_build_plan_limits')
    async def test_notify_build_plan_limits_exceeded_already_exceeded_sent_prev_month_only_storage(self, mock_send_notification):
        self.first_workspace.billing_details = {'notifications': {'plan_reaching': date.today() - timedelta(days=1),
                                                                  'plan_exceeded': date.today() - timedelta(days=40)}
                                                }
        self.first_workspace.save()
        await Users.notify_build_plan_limits(self.first_workspace.id, 1000, 10, 0.07, 0.34, True, None, 11)
        mock_send_notification.assert_called_once_with(self.first_workspace, 1000, 10, 0.07, 0.34,
                                                       True, None, 11)
        self.first_workspace = Users.get_by_id(self.first_workspace.id)
        self.assertEqual(self.first_workspace.billing_details['notifications'], {'plan_reaching': date.today() - timedelta(days=1),
                                                                                 'plan_exceeded': date.today()})
