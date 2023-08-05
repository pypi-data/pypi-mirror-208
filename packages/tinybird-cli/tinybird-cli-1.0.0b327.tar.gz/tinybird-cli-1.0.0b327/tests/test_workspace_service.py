import uuid
import tornado
from urllib.parse import urlencode
from unittest.mock import patch
import json


from tinybird.user import UserAccount, Users, scopes, User, UserWorkspaceRelationship
from tinybird.constants import CHCluster
from tinybird.workspace_service import WorkspaceService
from .views.base_test import BaseTest, TBApiProxyAsync, TBApiProxy
from .utils import exec_sql
from tinybird.ch import ch_table_details_async, ch_table_schema_async
from tinybird.data_connector import DataConnector
from tinybird.datasource import KafkaBranchDatasource


class TestWorkspaceService(BaseTest):

    def setUp(self):
        super(TestWorkspaceService, self).setUp()
        self.tb_api_proxy_async = TBApiProxyAsync(self)
        self.tb_api_proxy = TBApiProxy(self)
        self.user_account = UserAccount.get_by_id(self.USER_ID)

        # create origin workspace using cluster
        self.cluster = CHCluster('tinybird', User.default_database_server)
        workspace_name = f"ws_to_clone_{uuid.uuid4().hex}"
        self.workspace = self.tb_api_proxy.register_workspace(workspace_name, self.user_account, self.cluster)
        self.workspace_token = Users.get_token_for_scope(self.workspace, scopes.ADMIN)
        self.user_token = UserAccount.get_token_for_scope(self.user_account, scopes.AUTH)

    def assertEqualDatasource(self, datasource_a, datasource_b):
        attrs = ['id', 'name', '_description', 'tags', 'json_deserialization']
        for attr in attrs:
            self.assertEqual(getattr(datasource_a, attr), getattr(datasource_b, attr), attr)

    def assertEqualPipe(self, pipe_a, pipe_b):
        attrs = ['id', 'name', 'description', 'endpoint']
        for attr in attrs:
            self.assertEqual(getattr(pipe_a, attr), getattr(pipe_b, attr), attr)
        self.assertEqual(len(pipe_a.pipeline.nodes), len(pipe_b.pipeline.nodes))
        self.assertEqual(pipe_a.pipeline.to_json(), pipe_b.pipeline.to_json())

    def assertEqualToken(self, token_a, token_b):
        attrs = ['name', 'scopes', 'origin']
        for attr in attrs:
            self.assertEqual(token_a.to_dict()[attr], token_b.to_dict()[attr])

    async def _test_clone_datasources(self):
        # create new workspace to clone datasource
        workspace_name = f"ws_cloned_{uuid.uuid4().hex}"
        new_workspace = await self.tb_api_proxy_async.register_workspace(workspace_name, self.user_account,
                                                                         self.cluster)
        new_workspace_token = Users.get_token_for_scope(new_workspace, scopes.ADMIN)
        self.workspaces_to_delete.append(new_workspace)

        # clone datasource in new workspace
        await WorkspaceService.clone_datasources(self.workspace, new_workspace)
        new_workspace = User.get_by_id(new_workspace.id)
        self.assertEqual(len(self.workspace.get_datasources()), len(new_workspace.get_datasources()))
        cloned_datasource = new_workspace.get_datasource(self.datasource.id)
        self.assertEqualDatasource(self.datasource, cloned_datasource)
        table_details_a = await ch_table_details_async(self.datasource.id, self.workspace.database_server,
                                                       database=self.workspace.database)
        table_details_b = await ch_table_details_async(self.datasource.id, new_workspace.database_server,
                                                       database=new_workspace.database)
        self.assertEqual(table_details_a.to_json(), table_details_b.to_json())
        schema_a = await ch_table_schema_async(self.datasource.id, self.workspace.database_server,
                                               self.workspace.database)
        schema_b = await ch_table_schema_async(self.datasource.id, new_workspace.database_server,
                                               new_workspace.database)
        self.assertEqual(schema_a, schema_b)

        # check quarantine is available
        self.assertEqual(0, await self._query(new_workspace_token, f"select count() from {self.datasource.name}_quarantine"))

        # ds_ops_log
        self.expect_ops_log({'event_type': 'create',
                             'datasource_name': self.datasource.name,
                             'options': {'source': 'branch'}}, workspace=new_workspace)

    @tornado.testing.gen_test
    async def test_clone_datasources(self):
        # create datasource
        ds_name = f"ds_to_clone_{uuid.uuid4().hex}"
        schema = "uid UInt8, q Float64, v String, d DateTime"
        ds_response = await self.tb_api_proxy_async.create_datasource(
            self.workspace_token,
            ds_name,
            schema
        )
        self.workspace = User.get_by_id(self.workspace.id)
        self.datasource = self.workspace.get_datasource(ds_response['datasource']['id'])
        self.wait_for_datasource_replication(self.workspace, self.datasource)

        await self._test_clone_datasources()

    @tornado.testing.gen_test
    async def test_clone_datasources_ndjson(self):
        # create datasource
        ds_name = f"ds_to_clone_ndjson_{uuid.uuid4().hex}"
        schema = "id String `json:$.id`"
        ds_response = await self.tb_api_proxy_async.create_datasource(
            self.workspace_token,
            ds_name,
            schema,
            format='ndjson',
        )
        self.workspace = User.get_by_id(self.workspace.id)
        self.datasource = self.workspace.get_datasource(ds_response['datasource']['id'])
        self.wait_for_datasource_replication(self.workspace, self.datasource)

        await self._test_clone_datasources()

    @tornado.testing.gen_test
    async def test_clone_shared_datasources(self):
        # create new workspace to clone datasource
        sharing_workspace_name = f"ws_sharing_{uuid.uuid4().hex}"
        new_sharing_workspace = await self.tb_api_proxy_async.register_workspace(sharing_workspace_name, self.user_account, self.cluster)
        new_shared_workspace_token = Users.get_token_for_scope(new_sharing_workspace, scopes.ADMIN)
        self.workspaces_to_delete.append(new_sharing_workspace)

        # create datasource
        ds_name = f"ds_shared_to_clone_{uuid.uuid4().hex}"
        schema = "uid UInt8, q Float64, v String, d DateTime"
        ds_response = await self.tb_api_proxy_async.create_datasource(
            new_shared_workspace_token,
            ds_name,
            schema
        )
        new_sharing_workspace = User.get_by_id(new_sharing_workspace.id)
        self.datasource = new_sharing_workspace.get_datasource(ds_response['datasource']['id'])
        self.wait_for_datasource_replication(new_sharing_workspace, self.datasource)

        # share Data Sources between them
        await self.tb_api_proxy_async.share_datasource_with_another_workspace(
            token=self.user_token,
            datasource_id=self.datasource.id,
            origin_workspace_id=new_sharing_workspace.id,
            destination_workspace_id=self.workspace.id,
            expect_notification=False
        )

        self.workspace = Users.get_by_id(self.workspace.id)
        self.assertEqual(len(self.workspace.get_datasources()), 1)
        self.datasource = self.workspace.get_datasources()[0]
        self.assertEqual(self.datasource.name, f"{new_sharing_workspace.name}.{ds_name}")

        # create new workspace to clone datasource
        workspace_name = f"ws_cloned_{uuid.uuid4().hex}"
        new_workspace = await self.tb_api_proxy_async.register_workspace(workspace_name, self.user_account, self.cluster)
        new_workspace_token = Users.get_token_for_scope(new_workspace, scopes.ADMIN)
        self.workspaces_to_delete.append(new_workspace)

        # set as branch manually
        new_workspace.origin = self.workspace.id
        new_workspace.save()

        # clone datasource in new workspace
        await WorkspaceService.clone_datasources(self.workspace, new_workspace)
        new_workspace = User.get_by_id(new_workspace.id)
        self.assertEqual(len(self.workspace.get_datasources()), len(new_workspace.get_datasources()))
        cloned_datasource = new_workspace.get_datasource(self.datasource.id, include_read_only=True)
        self.assertEqualDatasource(self.datasource, cloned_datasource)
        table_details_a = await ch_table_details_async(self.datasource.id, new_sharing_workspace.database_server, database=new_sharing_workspace.database)
        table_details_b = await ch_table_details_async(self.datasource.id, new_workspace.database_server, database=new_workspace.database)
        self.assertEqual(table_details_a.to_json(), table_details_b.to_json())
        schema_a = await ch_table_schema_async(self.datasource.id, new_sharing_workspace.database_server, new_sharing_workspace.database)
        schema_b = await ch_table_schema_async(self.datasource.id, new_workspace.database_server, new_workspace.database)
        self.assertEqual(schema_a, schema_b)

        # check ds and quarantine are available
        self.assertEqual(0, await self._query(new_workspace_token, f"select count() from {cloned_datasource.name}"))
        self.assertEqual(0, await self._query(new_workspace_token, f"select count() from {cloned_datasource.name}_quarantine"))

    @tornado.testing.gen_test
    @patch('tinybird.kafka_utils.KafkaUtils.get_kafka_topic_group', return_value={'response': 'ok'})
    async def test_clone_kafka_datasource(self, _kafka_utils_mock):
        params = {
            'token': self.workspace_token,
            'kafka_bootstrap_servers': 'localhost:9093',
            'kafka_security_protocol': 'plaintext',
            'kafka_sasl_plain_username': '',
            'kafka_sasl_plain_password': '',
            'name': 'kafka_1',
            'service': 'kafka',
            'kafka_sasl_mechanism': 'PLAIN'
        }

        url = f"/v0/connectors?{urlencode(params)}"
        response = await self.tb_api_proxy_async._fetch(url, method='POST', data='')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)

        ds_name = f"ds_kafka_{uuid.uuid4().hex}"
        data_connector = DataConnector.get_by_id(result['id'])
        params = {
            'token': self.workspace_token,
            'mode': 'create',
            'name': ds_name,
            'connector': data_connector.id,
            'kafka_topic': 'kafka_topic',
            'kafka_group_id': 'kafka_group_id'
        }

        create_url = f"/v0/datasources?{urlencode(params)}"
        response = await self.tb_api_proxy_async._fetch(create_url, method='POST', data='')
        ds_response = json.loads(response.content)
        self.workspace = User.get_by_id(self.workspace.id)
        self.datasource = self.workspace.get_datasource(ds_response['datasource']['id'])
        self.wait_for_datasource_replication(self.workspace, self.datasource)

        # create new workspace to clone datasource
        workspace_name = f"ws_cloned_{uuid.uuid4().hex}"
        new_workspace = await self.tb_api_proxy_async.register_workspace(workspace_name, self.user_account, self.cluster)
        new_workspace_token = Users.get_token_for_scope(new_workspace, scopes.ADMIN)
        self.workspaces_to_delete.append(new_workspace)

        # set as branch manually
        new_workspace.origin = self.workspace.id
        new_workspace.save()

        # clone datasource in new workspace
        await WorkspaceService.clone_datasources(self.workspace, new_workspace)
        new_workspace = User.get_by_id(new_workspace.id)
        self.assertEqual(len(self.workspace.get_datasources()), len(new_workspace.get_datasources()))
        cloned_datasource = new_workspace.get_datasource(self.datasource.id, include_read_only=True)
        self.assertEqualDatasource(self.datasource, cloned_datasource)
        self.assertTrue(isinstance(cloned_datasource, KafkaBranchDatasource))
        self.assertNotEqual(cloned_datasource.to_json()['type'], 'kafka')
        self.assertEqual(self.datasource.to_dict().get('connector'), cloned_datasource.origin_connector_id)
        table_details_a = await ch_table_details_async(self.datasource.id, self.workspace.database_server,
                                                       database=self.workspace.database)
        table_details_b = await ch_table_details_async(self.datasource.id, new_workspace.database_server,
                                                       database=new_workspace.database)
        self.assertEqual(table_details_a.to_json(), table_details_b.to_json())
        schema_a = await ch_table_schema_async(self.datasource.id, self.workspace.database_server,
                                               self.workspace.database)
        schema_b = await ch_table_schema_async(self.datasource.id, new_workspace.database_server,
                                               new_workspace.database)
        self.assertEqual(schema_a, schema_b)

        # check ds and quarantine are available
        self.assertEqual(0, await self._query(new_workspace_token, f"select count() from {cloned_datasource.name}"))
        self.assertEqual(0, await self._query(new_workspace_token,
                                              f"select count() from {cloned_datasource.name}_quarantine"))

    @tornado.testing.gen_test
    async def test_clone_pipe_endpoint(self):
        self.create_test_datasource()
        # create pipe in workspace origin
        pipe_name = f"pipe_to_clone_{uuid.uuid4().hex}"
        Users.add_pipe(self.workspace, self.pipe_name, f"select * from {self.datasource.name}")
        await self.tb_api_proxy_async.create_pipe_endpoint(self.workspace, self.workspace_token, pipe_name,
                                                           "select count() from numbers(1,10)")
        self.workspace = User.get_by_id(self.workspace.id)
        pipe = self.workspace.get_pipe(pipe_name)

        # create new workspace to clone
        workspace_name = f"ws_cloned_{uuid.uuid4().hex}"
        new_workspace = await self.tb_api_proxy_async.register_workspace(workspace_name, self.user_account, self.cluster)
        new_workspace_token = Users.get_token_for_scope(new_workspace, scopes.ADMIN)
        self.workspaces_to_delete.append(new_workspace)

        # clone pipe in new workspace
        await WorkspaceService.clone_pipes(self.workspace, new_workspace)
        new_workspace = User.get_by_id(new_workspace.id)
        cloned_pipe = new_workspace.get_pipe(pipe.id)

        self.assertEqualPipe(cloned_pipe, pipe)

        # Request to pipe endpoint in new workspace
        params = {
            'token': new_workspace_token
        }
        response = await self.fetch_async(f'/v0/pipes/{pipe_name}.json?{urlencode(params)}')
        self.assertEqual(response.code, 200)

    @tornado.testing.gen_test
    async def test_clone_pipe_materializes(self):
        # create datasource
        ds_name = f"ds_to_clone_{uuid.uuid4().hex}"
        schema = "uid UInt8, q Float64, v String, d DateTime"
        ds_response = await self.tb_api_proxy_async.create_datasource(
            self.workspace_token,
            ds_name,
            schema
        )
        self.workspace = User.get_by_id(self.workspace.id)
        self.datasource = self.workspace.get_datasource(ds_response['datasource']['id'])
        self.wait_for_datasource_replication(self.workspace, self.datasource)

        # create a pipe's node with a view to materialize
        pipe_name = 'test_mat_view_to_clone'
        view_name = 'mat_view_node'
        target_ds_name = 'mat_view_node_ds'
        query = f'select q * 2 as b from {ds_name}'
        await self.tb_api_proxy_async.create_pipe_mv(self.workspace, self.workspace_token, pipe_name, view_name,
                                                     target_ds_name, query)
        self.workspace = User.get_by_id(self.workspace.id)
        pipe_mv = self.workspace.get_pipe(pipe_name)
        self.workspace.get_datasource(target_ds_name)

        # create new workspace to clone
        workspace_name = f"ws_cloned_{uuid.uuid4().hex}"
        new_workspace = await self.tb_api_proxy_async.register_workspace(workspace_name, self.user_account,
                                                                         self.cluster)
        Users.get_token_for_scope(new_workspace, scopes.ADMIN)
        self.workspaces_to_delete.append(new_workspace)

        # we need to clone datasources in new workspace first
        await WorkspaceService.clone_datasources(self.workspace, new_workspace)

        # clone pipe in new workspace
        new_workspace = User.get_by_id(new_workspace.id)
        await WorkspaceService.clone_pipes(self.workspace, new_workspace)
        new_workspace = User.get_by_id(new_workspace.id)
        cloned_pipe = new_workspace.get_pipe(pipe_mv.id)

        self.assertEqualPipe(cloned_pipe, pipe_mv)

        node_view_id = next(node.id for node in cloned_pipe.pipeline.nodes if node.materialized)

        query = f"""SELECT count() as c
                    FROM system.tables
                    WHERE
                        database = '{new_workspace.database}'
                        and name = '{node_view_id}'
                    FORMAT JSON"""
        r = exec_sql(new_workspace.database, query)
        table_exists = int(r['data'][0]['c']) == 1
        self.assertTrue(table_exists)

    @tornado.testing.gen_test
    async def test_clone_pipe_materializes_dependant_to_other_pipe(self):
        # create datasource
        ds_name = f"ds_to_clone_{uuid.uuid4().hex}"
        schema = "uid UInt8, q Float64, v String, d DateTime"
        ds_response = await self.tb_api_proxy_async.create_datasource(
            self.workspace_token,
            ds_name,
            schema
        )
        self.workspace = User.get_by_id(self.workspace.id)
        self.datasource = self.workspace.get_datasource(ds_response['datasource']['id'])
        self.wait_for_datasource_replication(self.workspace, self.datasource)

        # MV dependant node
        pipe_name = f"pipe_dependant_{uuid.uuid4().hex}"
        await self.tb_api_proxy_async.create_pipe_endpoint(self.workspace, self.workspace_token, pipe_name,
                                                           f"select * from {self.datasource.name}")
        self.workspace = User.get_by_id(self.workspace.id)

        # create a pipe's node with a view to materialize
        pipe_mv_name = 'test_mat_view_to_clone'
        view_name = 'mat_view_node'
        target_ds_name = 'mat_view_node_ds'
        query = f'select q * 2 as c from {pipe_name}'
        await self.tb_api_proxy_async.create_pipe_mv(self.workspace, self.workspace_token, pipe_mv_name, view_name,
                                                     target_ds_name, query)
        self.workspace = User.get_by_id(self.workspace.id)
        pipe_mv = self.workspace.get_pipe(pipe_mv_name)
        self.workspace.get_datasource(target_ds_name)

        self.workspace = User.get_by_id(self.workspace.id)

        # create new workspace to clone
        workspace_name = f"ws_cloned_{uuid.uuid4().hex}"
        new_workspace = await self.tb_api_proxy_async.register_workspace(workspace_name, self.user_account,
                                                                         self.cluster)
        Users.get_token_for_scope(new_workspace, scopes.ADMIN)
        self.workspaces_to_delete.append(new_workspace)

        # we need to clone datasources in new workspace first
        await WorkspaceService.clone_datasources(self.workspace, new_workspace)

        # clone pipe in new workspace
        new_workspace = User.get_by_id(new_workspace.id)
        await WorkspaceService.clone_pipes(self.workspace, new_workspace)
        new_workspace = User.get_by_id(new_workspace.id)
        cloned_pipe = new_workspace.get_pipe(pipe_mv.id)

        self.assertEqualPipe(cloned_pipe, pipe_mv)

        node_view_id = next(node.id for node in cloned_pipe.pipeline.nodes if node.materialized)

        query = f"""SELECT count() as c
                    FROM system.tables
                    WHERE
                        database = '{new_workspace.database}'
                        and name = '{node_view_id}'
                    FORMAT JSON"""
        r = exec_sql(new_workspace.database, query)
        table_exists = int(r['data'][0]['c']) == 1
        self.assertTrue(table_exists)

    @tornado.testing.gen_test
    async def test_clone_tokens(self):
        # create new workspace to clone
        workspace_name = f"ws_cloned_{uuid.uuid4().hex}"
        new_workspace = await self.tb_api_proxy_async.register_workspace(workspace_name, self.user_account,
                                                                         self.cluster)
        Users.get_token_for_scope(new_workspace, scopes.ADMIN)
        self.workspaces_to_delete.append(new_workspace)

        await WorkspaceService.clone_tokens(self.workspace, new_workspace)
        new_workspace = User.get_by_id(new_workspace.id)

        self.assertEqual(len(self.workspace.get_tokens()), len(new_workspace.get_tokens()))
        for token in self.workspace.get_tokens():
            branch_token = new_workspace.get_token(token.name)
            self.assertEqualToken(token, branch_token)

    @tornado.testing.gen_test
    async def test_compare_workspaces_no_changes(self):
        # create datasource
        ds_name = f"ds_to_clone_{uuid.uuid4().hex}"
        schema = "uid UInt8, q Float64, v String, d DateTime"
        ds_response = await self.tb_api_proxy_async.create_datasource(
            self.workspace_token,
            ds_name,
            schema
        )
        self.workspace = User.get_by_id(self.workspace.id)
        self.datasource = self.workspace.get_datasource(ds_response['datasource']['id'])
        self.wait_for_datasource_replication(self.workspace, self.datasource)

        # create pipe in workspace origin
        pipe_name = f"pipe_to_clone_{uuid.uuid4().hex}"
        await self.tb_api_proxy_async.create_pipe_endpoint(self.workspace, self.workspace_token, pipe_name,
                                                           "select count() from numbers(1,10)")
        self.workspace = User.get_by_id(self.workspace.id)
        self.workspace.get_pipe(pipe_name)

        # create new workspace to clone
        workspace_name = f"ws_cloned_{uuid.uuid4().hex}"
        new_workspace = await self.tb_api_proxy_async.register_workspace(workspace_name, self.user_account,
                                                                         self.cluster)
        Users.get_token_for_scope(new_workspace, scopes.ADMIN)
        self.workspaces_to_delete.append(new_workspace)

        await WorkspaceService.clone_datasources(self.workspace, new_workspace)
        await WorkspaceService.clone_pipes(self.workspace, new_workspace)

        self.workspace = User.get_by_id(self.workspace.id)
        new_workspace = User.get_by_id(new_workspace.id)

        workspace_diff = await WorkspaceService.compare_workspaces(self.workspace, new_workspace)
        self.assertEqual(workspace_diff.datasources, {'new': [], 'modified': [], 'deleted': [], 'only_metadata': []})
        self.assertEqual(workspace_diff.pipes, {'new': [], 'modified': [], 'deleted': [], 'only_metadata': []})

    @tornado.testing.gen_test
    async def test_compare_workspaces_deleted_resources(self):
        # create datasource
        ds_name = f"ds_to_clone_{uuid.uuid4().hex}"
        schema = "uid UInt8, q Float64, v String, d DateTime"
        ds_response = await self.tb_api_proxy_async.create_datasource(
            self.workspace_token,
            ds_name,
            schema
        )
        self.workspace = User.get_by_id(self.workspace.id)
        self.datasource = self.workspace.get_datasource(ds_response['datasource']['id'])
        self.wait_for_datasource_replication(self.workspace, self.datasource)

        # create pipe in workspace origin
        pipe_name = f"pipe_to_clone_{uuid.uuid4().hex}"
        await self.tb_api_proxy_async.create_pipe_endpoint(self.workspace, self.workspace_token, pipe_name,
                                                           "select count() from numbers(1,10)")
        self.workspace = User.get_by_id(self.workspace.id)
        pipe = self.workspace.get_pipe(pipe_name)

        # create new workspace to clone
        workspace_name = f"ws_cloned_{uuid.uuid4().hex}"
        new_workspace = await self.tb_api_proxy_async.register_workspace(workspace_name, self.user_account,
                                                                         self.cluster)
        self.workspaces_to_delete.append(new_workspace)

        workspace_diff = await WorkspaceService.compare_workspaces(self.workspace, new_workspace)
        self.assertEqual(workspace_diff.datasources, {'new': [], 'modified': [], 'deleted': [{'id': self.datasource.id,
                                                                                              'name': self.datasource.name}],
                                                      'only_metadata': []})
        self.assertEqual(workspace_diff.pipes, {'new': [], 'modified': [], 'deleted': [{'id': pipe.id, 'name': pipe.name}], 'only_metadata': []})

    @tornado.testing.gen_test
    async def test_compare_workspaces_new_resources(self):
        # create new workspace to clone
        workspace_name = f"ws_cloned_{uuid.uuid4().hex}"
        new_workspace = await self.tb_api_proxy_async.register_workspace(workspace_name, self.user_account,
                                                                         self.cluster)
        self.workspaces_to_delete.append(new_workspace)

        new_workspace_token = Users.get_token_for_scope(new_workspace, scopes.ADMIN)

        # create datasource
        ds_name = f"ds_to_clone_{uuid.uuid4().hex}"
        schema = "uid UInt8, q Float64, v String, d DateTime"
        ds_response = await self.tb_api_proxy_async.create_datasource(
            new_workspace_token,
            ds_name,
            schema
        )
        new_workspace = User.get_by_id(new_workspace.id)
        self.datasource = new_workspace.get_datasource(ds_response['datasource']['id'])
        self.wait_for_datasource_replication(new_workspace, self.datasource)

        # create pipe in workspace origin
        pipe_name = f"pipe_to_clone_{uuid.uuid4().hex}"
        await self.tb_api_proxy_async.create_pipe_endpoint(new_workspace, new_workspace_token, pipe_name,
                                                           "select count() from numbers(1,10)")
        self.workspace = User.get_by_id(self.workspace.id)
        new_workspace = User.get_by_id(new_workspace.id)
        pipe = new_workspace.get_pipe(pipe_name)

        workspace_diff = await WorkspaceService.compare_workspaces(self.workspace, new_workspace)
        self.assertEqual(workspace_diff.datasources, {'new': [{'id': self.datasource.id, 'name': self.datasource.name}], 'modified': [], 'deleted': [], 'only_metadata': []})
        self.assertEqual(workspace_diff.pipes, {'new': [{'id': pipe.id, 'name': pipe.name}], 'modified': [], 'deleted': [], 'only_metadata': []})

    @tornado.testing.gen_test
    async def test_compare_workspaces_modified_resources(self):
        # create datasource
        ds_name = f"ds_to_clone_{uuid.uuid4().hex}"
        schema = "uid UInt8, q Float64, v String, d DateTime"
        ds_response = await self.tb_api_proxy_async.create_datasource(
            self.workspace_token,
            ds_name,
            schema
        )
        self.workspace = User.get_by_id(self.workspace.id)
        self.datasource = self.workspace.get_datasource(ds_response['datasource']['id'])
        self.wait_for_datasource_replication(self.workspace, self.datasource)

        # create pipe in workspace origin
        pipe_name = f"pipe_to_clone_{uuid.uuid4().hex}"
        await self.tb_api_proxy_async.create_pipe_endpoint(self.workspace, self.workspace_token, pipe_name,
                                                           "select count() from numbers(1,10)")
        self.workspace = User.get_by_id(self.workspace.id)
        self.workspace.get_pipe(pipe_name)

        # create new workspace to clone
        workspace_name = f"ws_cloned_{uuid.uuid4().hex}"
        new_workspace = await self.tb_api_proxy_async.register_workspace(workspace_name, self.user_account,
                                                                         self.cluster)
        Users.get_token_for_scope(new_workspace, scopes.ADMIN)
        self.workspaces_to_delete.append(new_workspace)

        await WorkspaceService.clone_datasources(self.workspace, new_workspace)
        await WorkspaceService.clone_pipes(self.workspace, new_workspace)

        self.workspace = User.get_by_id(self.workspace.id)
        new_workspace = User.get_by_id(new_workspace.id)

        # modify datasource
        sql = f"ALTER TABLE {new_workspace.database}.{self.datasource.id} ADD COLUMN added UInt32 FIRST;"
        exec_sql(new_workspace.database, sql)

        # modify pipe
        pipe = new_workspace.get_pipe(pipe_name)
        await Users.drop_endpoint_of_pipe_node_async(new_workspace.id, pipe.id, pipe.pipeline.last().id)

        new_workspace = User.get_by_id(new_workspace.id)

        workspace_diff = await WorkspaceService.compare_workspaces(self.workspace, new_workspace)
        self.assertEqual(workspace_diff.datasources, {'new': [], 'modified': [{'id': self.datasource.id, 'name': self.datasource.name}], 'deleted': [], 'only_metadata': []})
        self.assertEqual(workspace_diff.pipes, {'new': [], 'modified': [{'id': pipe.id, 'name': pipe.name}], 'deleted': [], 'only_metadata': []})

    @tornado.testing.gen_test
    async def test_compare_workspaces_only_metadata_modified_resources(self):
        # create datasource
        ds_name = f"ds_to_clone_{uuid.uuid4().hex}"
        schema = "uid UInt8, q Float64, v String, d DateTime"
        ds_response = await self.tb_api_proxy_async.create_datasource(
            self.workspace_token,
            ds_name,
            schema
        )
        self.workspace = User.get_by_id(self.workspace.id)
        self.datasource = self.workspace.get_datasource(ds_response['datasource']['id'])
        self.wait_for_datasource_replication(self.workspace, self.datasource)

        # create pipe in workspace origin
        pipe_name = f"pipe_to_clone_{uuid.uuid4().hex}"
        await self.tb_api_proxy_async.create_pipe_endpoint(self.workspace, self.workspace_token, pipe_name,
                                                           "select count() from numbers(1,10)")
        self.workspace = User.get_by_id(self.workspace.id)
        self.workspace.get_pipe(pipe_name)

        # create new workspace to clone
        workspace_name = f"ws_cloned_{uuid.uuid4().hex}"
        new_workspace = await self.tb_api_proxy_async.register_workspace(workspace_name, self.user_account,
                                                                         self.cluster)
        Users.get_token_for_scope(new_workspace, scopes.ADMIN)
        self.workspaces_to_delete.append(new_workspace)

        await WorkspaceService.clone_datasources(self.workspace, new_workspace)
        await WorkspaceService.clone_pipes(self.workspace, new_workspace)

        self.workspace = User.get_by_id(self.workspace.id)
        new_workspace = User.get_by_id(new_workspace.id)

        pipe = new_workspace.get_pipe(pipe_name)
        await Users.alter_datasource_name(new_workspace, self.datasource.id, f"modified_name_{self.datasource.name}")
        await Users.alter_pipe_async(new_workspace, pipe.id, f"modified_name_{pipe_name}")
        new_workspace = User.get_by_id(new_workspace.id)

        workspace_diff = await WorkspaceService.compare_workspaces(self.workspace, new_workspace)
        self.assertEqual(workspace_diff.datasources, {'new': [], 'modified': [], 'deleted': [], 'only_metadata': [{'id': self.datasource.id, 'name': self.datasource.name}]})
        self.assertEqual(workspace_diff.pipes, {'new': [], 'modified': [], 'deleted': [], 'only_metadata': [{'id': pipe.id, 'name': pipe.name}]})

    @tornado.testing.gen_test
    async def test_compare_workspaces_no_changes_with_shared_datasource(self):
        sharing_workspace_name = f"ws_sharing_{uuid.uuid4().hex}"
        new_sharing_workspace = await self.tb_api_proxy_async.register_workspace(sharing_workspace_name,
                                                                                 self.user_account, self.cluster)
        new_shared_workspace_token = Users.get_token_for_scope(new_sharing_workspace, scopes.ADMIN)
        self.workspaces_to_delete.append(new_sharing_workspace)

        # create datasource
        ds_name = f"ds_shared_to_clone_{uuid.uuid4().hex}"
        schema = "uid UInt8, q Float64, v String, d DateTime"
        ds_response = await self.tb_api_proxy_async.create_datasource(
            new_shared_workspace_token,
            ds_name,
            schema
        )
        new_sharing_workspace = User.get_by_id(new_sharing_workspace.id)
        self.datasource = new_sharing_workspace.get_datasource(ds_response['datasource']['id'])
        self.wait_for_datasource_replication(new_sharing_workspace, self.datasource)

        # share Data Sources between them
        await self.tb_api_proxy_async.share_datasource_with_another_workspace(
            token=self.user_token,
            datasource_id=self.datasource.id,
            origin_workspace_id=new_sharing_workspace.id,
            destination_workspace_id=self.workspace.id,
            expect_notification=False
        )

        self.workspace = Users.get_by_id(self.workspace.id)
        self.assertEqual(len(self.workspace.get_datasources()), 1)
        self.datasource = self.workspace.get_datasources()[0]
        self.assertEqual(self.datasource.name, f"{new_sharing_workspace.name}.{ds_name}")

        # create pipe in workspace origin
        pipe_name = f"pipe_to_clone_{uuid.uuid4().hex}"
        await self.tb_api_proxy_async.create_pipe_endpoint(self.workspace, self.workspace_token, pipe_name,
                                                           "select count() from numbers(1,10)")
        self.workspace = User.get_by_id(self.workspace.id)
        self.workspace.get_pipe(pipe_name)

        # create new workspace to clone
        workspace_name = f"ws_cloned_{uuid.uuid4().hex}"
        new_workspace = await self.tb_api_proxy_async.register_workspace(workspace_name, self.user_account,
                                                                         self.cluster)
        Users.get_token_for_scope(new_workspace, scopes.ADMIN)
        self.workspaces_to_delete.append(new_workspace)

        await WorkspaceService.clone_datasources(self.workspace, new_workspace)
        await WorkspaceService.clone_pipes(self.workspace, new_workspace)

        self.workspace = User.get_by_id(self.workspace.id)
        new_workspace = User.get_by_id(new_workspace.id)

        workspace_diff = await WorkspaceService.compare_workspaces(self.workspace, new_workspace)
        self.assertEqual(workspace_diff.datasources, {'new': [], 'modified': [], 'deleted': [], 'only_metadata': []})
        self.assertEqual(workspace_diff.pipes, {'new': [], 'modified': [], 'deleted': [], 'only_metadata': []})

    @tornado.testing.gen_test
    async def test_clone_members(self):
        # new user account to add to workspace
        new_user = UserAccount.register(f'new_user_{uuid.uuid4().hex}@example.com', 'pass')
        self.users_to_delete.append(new_user)

        params = {
            'token': self.user_token,
            'operation': 'add',
            'users': new_user.email
        }
        url = f"/v0/workspaces/{self.workspace.id}/users?{urlencode(params)}"

        response = await self.fetch_async(url, method='PUT', body='')
        self.assertEqual(response.code, 200)
        result = json.loads(response.body)
        self.assertEqual(len(result['members']), 2)

        # create new workspace to clone
        workspace_name = f"ws_cloned_{uuid.uuid4().hex}"
        new_workspace = await self.tb_api_proxy_async.register_workspace(workspace_name, self.user_account,
                                                                         self.cluster)
        Users.get_token_for_scope(new_workspace, scopes.ADMIN)
        self.workspaces_to_delete.append(new_workspace)

        await WorkspaceService.clone_members(self.workspace, new_workspace)
        new_workspace = User.get_by_id(new_workspace.id)
        self.workspace = User.get_by_id(self.workspace.id)

        workspace_members = UserWorkspaceRelationship.get_by_workspace(self.workspace.id)
        new_workspace_members = UserWorkspaceRelationship.get_by_workspace(new_workspace.id)

        self.assertEqual(len(workspace_members), len(new_workspace_members))
        for member in workspace_members:
            found = False
            for new_workspace_member in new_workspace_members:
                if member.user_id == new_workspace_member.user_id:
                    found = True
                    self.assertEqual(member.relationship, new_workspace_member.relationship)

            self.assertTrue(found, "Not all members found")
