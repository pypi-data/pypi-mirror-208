import click
import os
import tornado
import requests
import tempfile
import shutil
from pathlib import Path

from urllib.parse import urlencode
from .views.base_test import BaseTest

from tinybird.ch import ch_get_replicas_for_table_sync
from tinybird.user import Users, User
from tinybird.token_scope import scopes

from tinybird.syncasync import sync_to_async
from tinybird.datafile import folder_push, folder_pull
from tinybird.client import TinyB

from io import StringIO


class TestProjects(BaseTest):

    def setUp(self):
        super().setUp()
        u = Users.get_by_id(self.WORKSPACE_ID)
        self.u = u
        self.admin_token = Users.get_token_for_scope(u, scopes.ADMIN)
        self.finished = False
        self.error = None

    async def __push_folder(self, folder, tag='', upload_fixtures=False, push_deps=True, filenames=None):
        self.finished = False
        self.error = None

        prev_cwd = os.getcwd()
        os.chdir(folder)

        tb_client = TinyB(self.admin_token, self.get_host())

        try:
            await folder_push(
                tb_client,
                folder=folder,
                force=True,
                push_deps=push_deps,
                tag=tag,
                upload_fixtures=upload_fixtures,
                filenames=filenames,
                wait=True)
        except Exception as e:
            self.error = e
        finally:
            os.chdir(prev_cwd)
            self.finished = True
        if self.error:
            raise self.error

    async def __pull_folder(self, folder, tag=None, match=None):
        self.finished = False
        self.error = None

        host = self.get_host()
        cl = TinyB(self.admin_token, host)
        try:
            await folder_pull(
                cl,
                folder=folder,
                auto=False,
                match=match,
                tag=tag,
                force=False)
        except Exception as e:
            self.error = e
        finally:
            self.finished = True

    async def push_data(self, name, data, mode='replace'):
        params = {
            'name': name,
            'token': self.admin_token,
            'mode': mode
        }
        create_url = f"/v0/datasources?{urlencode(params)}"
        post = sync_to_async(requests.post, thread_sensitive=False)
        r = await post(self.get_url(create_url), data=data)
        self.assertEqual(r.status_code, 200, r.content)
        return r

    async def _fetch(self, path, method='get', **kwargs):
        get = sync_to_async(getattr(requests, method.lower()), thread_sensitive=False)
        response = await get(self.get_url(path), **kwargs)
        return response

    @tornado.testing.gen_test
    async def test_join_tables(self):
        ch_get_replicas_for_table = sync_to_async(ch_get_replicas_for_table_sync, thread_sensitive=False)

        project_dir = os.path.dirname(__file__) + '/projects/test_view_to_join'
        await self.__push_folder(project_dir)

        # replace data
        s = StringIO("""a,b\n1,e\n2,d\n3,d\n4,d\n1,f""")
        await self.push_data('test', s)

        ds = Users.get_datasource(self.u, 'test')
        replicas = await ch_get_replicas_for_table(self.u.database_server, self.u.database, ds.id, self.u.cluster)
        self.assertTrue(len(replicas) >= 2)
        for database_server in replicas:
            with User.transaction(self.u.id) as user:
                user.database_server = database_server
            params = {
                'q': "select joinGet('test_join', 's', 'd') as key format JSON",
                'token': self.admin_token
            }
            response = await self._fetch(f'/v0/sql?{urlencode(params)}')
            self.assertEqual(response.status_code, 200, response.content)
            result = response.json()
            self.assertEqual(result['data'][0], {'key': 9}, f'{database_server} is not replicated')

    @tornado.testing.gen_test
    async def test_fail_to_parse_tsv(self):
        await self.__push_folder(os.path.dirname(__file__) + '/projects/test_fail_to_parse_tsv', tag='dev', upload_fixtures=True)
        params = {
            'q': "select count() c from dev__wikipedia_quarantine",
            'token': self.admin_token
        }
        response = await self._fetch(f'/v0/sql?{urlencode(params)}')
        result = response.json()
        self.assertEqual(result, 4, result)

    @tornado.testing.gen_test
    async def test_should_upload_last_versions_from_scracth(self):
        await self.__push_folder(os.path.dirname(__file__) + '/projects/test_versions')

        params = {
            'token': self.admin_token
        }
        response = await self._fetch(f'/v0/datasources/test__v1?{urlencode(params)}')
        self.assertEqual(response.status_code, 200, response)
        response = await self._fetch(f'/v0/pipes/transform_data__v0?{urlencode(params)}')
        self.assertEqual(response.status_code, 200, response)
        response = await self._fetch(f'/v0/pipes/test_endpoint__v1?{urlencode(params)}')
        self.assertEqual(response.status_code, 200, response)

    @tornado.testing.gen_test
    async def test_should_use_project_versions(self):

        # create a new version and push the project
        params = {
            'token': self.admin_token,
            'name': 'test__v2',
            'schema': 'a Int32, b Float64, c String'
        }
        response = await self._fetch(f'/v0/datasources/?{urlencode(params)}', method='POST', data='')

        await self.__push_folder(os.path.dirname(__file__) + '/projects/test_versions')
        params = {
            'token': self.admin_token
        }
        response = await self._fetch(f'/v0/pipes/test_endpoint__v1?{urlencode(params)}')
        r = response.json()
        # here it must use v1 because that's what we have in the project
        self.assertEqual('test__v1' in r['nodes'][0]['sql'], True, r)

        response = await self._fetch(f'/v0/pipes/transform_data__v0?{urlencode(params)}')
        r = response.json()
        # here it must use v1 because that's what we have in the project
        self.assertEqual('test__v1' in r['nodes'][0]['sql'], True, r)

    @tornado.testing.gen_test
    async def test_should_push_only_one_file(self):
        params = {
            'token': self.admin_token,
            'name': 'ony_one_file__test__v1',
            'schema': 'a Int32, b Float64, c String'
        }
        response = await self._fetch(f'/v0/datasources/?{urlencode(params)}', method='POST', data='')

        folder_path = os.path.dirname(__file__) + '/projects/test_versions'
        await self.__push_folder(
            folder_path,
            filenames=[folder_path + "/endpoints/test_endpoint.pipe"],
            tag='ony_one_file',
            push_deps=False
        )
        params = {
            'token': self.admin_token
        }
        response = await self._fetch(f'/v0/pipes/ony_one_file__test_endpoint__v1?{urlencode(params)}')
        self.assertEqual(response.status_code, 200, response)
        r = response.json()
        # here it must use v1 because that's what we have in the project (even if it's not pushed)
        self.assertEqual('ony_one_file__test__v1' in r['nodes'][0]['sql'], True, r)

    @tornado.testing.gen_test
    async def test_should_upload_last_versions_with_tag(self):
        await self.__push_folder(os.path.dirname(__file__) + '/projects/test_versions', tag='mybranch')

        params = {
            'token': self.admin_token
        }
        response = await self._fetch(f'/v0/datasources/mybranch__test__v1?{urlencode(params)}')
        self.assertEqual(response.status_code, 200, response)
        response = await self._fetch(f'/v0/pipes/mybranch__transform_data__v0?{urlencode(params)}')
        self.assertEqual(response.status_code, 200, response)
        response = await self._fetch(f'/v0/pipes/mybranch__test_endpoint__v1?{urlencode(params)}')
        self.assertEqual(response.status_code, 200, response)
        response = await self._fetch(f'/v0/datasources/test__v1?{urlencode(params)}')
        self.assertEqual(response.status_code, 404, response)

    @tornado.testing.gen_test
    async def test_should_pull_last_versions(self):
        params = {
            'token': self.admin_token,
            'name': 'test__v2',
            'schema': 'a Int32, b Float64, c String'
        }
        await self._fetch(f'/v0/datasources/?{urlencode(params)}', method='POST', data='')

        params = {
            'token': self.admin_token,
            'name': 'test_pipe__v1',
            'sql': 'select count() from test__v2'
        }
        await self._fetch(f'/v0/pipes/?{urlencode(params)}', method='POST', data='')

        tmppath = tempfile.mkdtemp()
        await self.__pull_folder(tmppath)
        project_folder = Path(tmppath)
        ds = project_folder / 'test.datasource'
        self.assertEqual(ds.exists(), True, list(project_folder.iterdir()))
        with open(ds) as file:
            contents = file.read()
        self.assertEqual('VERSION 2' in contents, True, contents)

        ds = project_folder / 'test_pipe.pipe'
        with open(ds) as file:
            contents = file.read()
        self.assertEqual(ds.exists(), True, list(project_folder.iterdir()))
        self.assertEqual('VERSION 1' in contents, True, contents)
        shutil.rmtree(tmppath)

    @tornado.testing.gen_test
    async def test_should_use_server_missing_deps(self):
        # create a datasource which is missing locally so in the push is used
        params = {
            'token': self.admin_token,
            'name': 'test_missing_locally__v1',
            'schema': 'a Int32, b Float64, c String'
        }
        await self._fetch(f'/v0/datasources/?{urlencode(params)}', method='POST', data='')

        await self.__push_folder(os.path.dirname(__file__) + '/projects/test_missing_deps')

        params = {
            'token': self.admin_token
        }
        response = await self._fetch(f'/v0/pipes/test_endpoint__v1?{urlencode(params)}')
        self.assertEqual(response.status_code, 200, response)
        r = response.json()
        # here it must use v1 because that's what we have in the project (even if it's not pushed)
        self.assertEqual('test_missing_locally__v1' in r['nodes'][0]['sql'], True, r)

    @tornado.testing.gen_test
    async def test_should_push_matview_and_check_engine(self):
        await self.__push_folder(os.path.dirname(__file__) + '/projects/test_mat_views')

    @tornado.testing.gen_test
    async def test_datasource_deps(self):
        with self.assertRaisesRegex(Exception, r"Resource \'worldwide_stores_join_by_country\' not found"):
            await self.__push_folder(os.path.dirname(__file__) + '/projects/ds_deps', filenames=['sales.datasource'], push_deps=False)

        await self.__push_folder(os.path.dirname(__file__) + '/projects/ds_deps', filenames=['sales.datasource'], push_deps=True)
        params = {
            'token': self.admin_token
        }
        for ds in ('sales', 'stores_join', 'worldwide_stores_join_by_country'):
            response = await self._fetch(f'/v0/datasources/{ds}?{urlencode(params)}')
            self.assertEqual(response.status_code, 200, response)

    @tornado.testing.gen_test
    async def test_wrong_engine_vars(self):
        with self.assertRaisesRegex(Exception, r"ENGINE_WRONG_KEY is not a valid option"):
            await self.__push_folder(os.path.dirname(__file__) + '/projects/test_datafiles', filenames=['wrong_engine_var.datasource'], push_deps=False)

    @tornado.testing.gen_test
    async def test_sql_injection_in_engine(self):
        with self.assertRaisesRegex(Exception, r"Failed creating Data Source: Invalid data source structure: CREATE TABLE: Unsupported CREATE AS query"):
            await self.__push_folder(os.path.dirname(__file__) + '/projects/test_datafiles',
                                     filenames=['engine_sql_injection.datasource'], push_deps=False)

    @tornado.testing.gen_test
    async def test_sql_injection_in_materialized_column(self):
        with self.assertRaisesRegex(click.exceptions.ClickException,
                                    r"DB::Exception: Usage of function remote is restricted"):
            await self.__push_folder(os.path.dirname(__file__) + '/projects/test_datafiles',
                                     filenames=['materialized_sql_injection.datasource'], push_deps=False)
