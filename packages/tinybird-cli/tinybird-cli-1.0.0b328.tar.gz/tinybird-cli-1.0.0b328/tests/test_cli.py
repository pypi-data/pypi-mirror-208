import contextlib
import glob
import json
import os
import re
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlencode

import pytest
import unittest.mock
from unittest.mock import patch, AsyncMock
import requests
import tornado.testing
from _pytest.monkeypatch import MonkeyPatch
from click.testing import CliRunner

from tests.utils import HTTP_ADDRESS
from tinybird.ch import HTTPClient
from tinybird.ch_utils.errors import CHErrors
from tinybird.ch_utils.exceptions import CHException
from tinybird.client import (MAX_GET_LENGTH, AuthException,
                             AuthNoTokenException, TinyB)
from tinybird.feature_flags import FeatureFlagWorkspaces
from tinybird.feedback_manager import FeedbackManager
from tinybird.job import Job, JobExecutor, JobStatus
from tinybird.kafka_utils import KafkaUtils
from tinybird.syncasync import sync_to_async
from tinybird.tb_cli import cli
from tinybird.tb_cli_modules.common import PROJECT_PATHS, SUPPORTED_FORMATS
from tinybird.tb_cli_modules.telemetry import \
    _get_helper as get_telemetry_helper
from tinybird.tb_cli_modules.telemetry import flush_telemetry
from tinybird.token_scope import scopes
from tinybird.user import (User, UserAccount, UserAccounts, UserDoesNotExist,
                           Users)
from tinybird.views.api_workspaces import APIWorkspaceCreationHandler
from tinybird.ingest.external_datasources.admin import generate_account_name

from .conftest import CH_ADDRESS
from .test_jobs import FakeTestJob
from .utils import (get_finalised_job_async,
                    wait_until_job_is_in_expected_status_async)
from .views.base_test import BaseTest, TBApiProxyAsync, matches

from tinybird.ingest.external_datasources.connector import CDKConnector
from tinybird_cdk.connectors.snowflake import Role, Integration


def get_resource_path(fixture_file_name) -> str:
    return f'{os.path.dirname(__file__)}/cli/{fixture_file_name}'


schema_expectations = {
    'sales_new': """SCHEMA >
    `cod_brand` Int16,
    `local_timeplaced` DateTime,
    `country` String,
    `purchase_location` Int16""",
    'events': """SCHEMA >
    date DateTime `json:$.date`,
    event String `json:$.event`,
    extra_data_city String `json:$.extra_data.city`,
    product_id String `json:$.product_id`,
    user_id Int32 `json:$.user_id`,
    extra_data_price Nullable(Float32) `json:$.extra_data.price`,
    extra_data_term Nullable(String) `json:$.extra_data.term`""",
    'hello_world': """SCHEMA >
    date DateTime `json:$.date`,
    id Int16 `json:$.id`,
    name String `json:$.name`""", }

schema_expectations['sales'] = schema_expectations['sales_new']


async def used_tables_mock(self, sql, raising=False):
    local = self._sql_get_used_tables_local(sql, raising)
    remote = await self._sql_get_used_tables_remote(sql, raising)
    assert local == remote
    return local


async def replace_tables_mock(self, q, replacements):
    local = self._replace_tables_local(q, replacements)
    remote = await self._replace_tables_remote(q, replacements)
    assert local == remote
    return local


class TestCLI(BaseTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Here we are going to replace the sql_get_used_tables and replace_tables methods to do the work twice,
        # one with the local module and one with the remote server and make sure the results are the same
        cls.patch_used_tables = patch(target="tinybird.client.TinyB.sql_get_used_tables", new=used_tables_mock)
        cls.patch_replace_tables = patch(target="tinybird.client.TinyB.replace_tables", new=replace_tables_mock)
        cls.patch_used_tables.start()
        cls.patch_replace_tables.start()

        cls.CLI_PROJECT_PATH = f'{os.path.dirname(__file__)}/cli/cli-project-{uuid.uuid4().hex}/'

    @classmethod
    def tearDownClass(cls):
        cls.patch_used_tables.stop()
        cls.patch_replace_tables.stop()
        super().tearDownClass()

    def setUp(self) -> None:
        self.partition_key = 'PARTITION BY (a%1000)'

        #  We are monkey patching _RandomNameSequence to avoid creating temporal files with double underscores `__` as this can lead to issues with the datafile.get_name_tag_version
        #  So to avoid flaky tests failing as a result of this, we are avoiding to use the `__` in the test datafiles
        self.mpatch = MonkeyPatch()
        self.mpatch.setattr('tempfile._RandomNameSequence.characters', "abcdefghijklmnopqrstuvwxyz0123456789")

        super().setUp()
        self.runner = CliRunner()
        self.tb = cli
        self.workspace = Users.get_by_id(self.WORKSPACE_ID)
        self.user_account = UserAccount.get_by_id(self.USER_ID)
        self.user_admin_token = UserAccount.get_token_for_scope(self.user_account, scopes.AUTH)
        self.admin_token = Users.get_token_for_scope(self.workspace, scopes.ADMIN_USER)
        self.user_token = self.user_account.get_token_for_scope(scopes.AUTH)
        self.workspace_admin_token = Users.get_token_for_scope(self.workspace, scopes.ADMIN)
        self.runner.invoke = sync_to_async(self.runner.invoke, thread_sensitive=False)
        self.host = self.get_host()
        self.api_host = self.get_host()
        self._clean_cli_project_dir()
        self.workdir = self._get_resource_path("../../")
        os.mkdir(f'{self.CLI_PROJECT_PATH}')
        os.chdir(self.CLI_PROJECT_PATH)
        shutil.copytree(self._get_resource_path("fixtures"), f'{self.CLI_PROJECT_PATH}/fixtures')
        self.tmp_files = []

        self.create_test_datasource(partition_key=self.partition_key)

    def tearDown(self) -> None:
        self.mpatch.undo()
        self._clean_cli_project_dir()
        with contextlib.suppress(FileNotFoundError):
            os.remove('.tinyb')
        os.chdir(self.workdir)
        self.remove_tmp_file()
        super().tearDown()

    def remove_tmp_file(self) -> None:
        for f in self.tmp_files:
            os.unlink(f)
            assert not os.path.exists(f)

    def create_tmp_file(
        self,
        suffix: str,
        encoding: str = 'utf-8'
    ) -> Tuple[Any, str]:
        """
            Create a temporary file with the given suffix, but without __ to avoid issues with datafile.get_name_tag_version
        """
        f = tempfile.NamedTemporaryFile(suffix=suffix, delete=False, mode='w+', encoding=encoding)
        name = os.path.basename(f.name).rsplit('.', 1)[0]

        self.tmp_files.append(f.name)

        return (f, name)

    async def _tb(
        self,
        args: Optional[Iterable[str]] = None,
        input: Optional[str] = None,
        env: Optional[Dict[str, Any]] = None,
        replace_new_line: bool = True,
        assert_exit_code: int = 0
    ) -> str:
        """Calls the CLI entry point with the `args` passed.

           Also:
           - Allows to pass an `input` string, in case you need to interactively
           control the operation.
           - Allows to pass a custom dict with environment variables in `env`.
           - `replace_new_line` controls how you get the resulting output.
           - `assert_exit_code` indicates the expected exit code for the process
             (0 by default)
        """

        result = await self.runner.invoke(self.tb, args, input, env, catch_exceptions=False)
        self.assertEqual(result.exit_code, assert_exit_code, result.stdout_bytes.decode("utf-8"))

        res = result.stdout_bytes.decode("utf-8")
        return res.replace('\n', '') if replace_new_line else res

    async def _auth(
        self,
        token: Optional[str] = None,
        env: Optional[Dict[str, Any]] = None,
        assert_exit_code: int = 0
    ) -> None:
        if token is None:
            token = self.admin_token
        _ = await self._tb(["auth", f'--host={self.host}'],
                           input=token, env=env,
                           assert_exit_code=assert_exit_code)

    def _clean_output(self, message: str) -> str:
        return re.sub(r'\033\[[0-9;]+m', '', message).strip().replace('\n', '')

    def _get_resource_path(self, filename: str) -> str:
        return f'{os.path.dirname(__file__)}/cli/{filename}'

    def _get_fixture_path(self, filename: str) -> str:
        return f'{os.path.dirname(__file__)}/fixtures/{filename}'

    def _assert_feedback_output(
        self,
        feedback: Iterable[str],
        output: Iterable[str],
        not_in: bool = False
    ) -> None:
        if feedback:
            for message in feedback:
                clean_message = self._clean_output(message)
                if not_in:
                    self.assertNotIn(clean_message, output)
                else:
                    self.assertIn(clean_message, output)

    def _clean_cli_project_dir(self) -> None:
        try:
            shutil.rmtree(f'{self.CLI_PROJECT_PATH}')
        except FileNotFoundError:
            pass

    def _clean_table(self, table: str) -> str:
        return table.replace('|', '').replace('-', '').replace(' ', '')

    def _get_job_from_response(
        self,
        response: str
    ) -> List[re.Match]:
        return re.findall(r"\/v0\/jobs\/(\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b)", response)

    async def check_endpoint_name(
        self,
        pipe_name: str,
        expected_endpoint_name: str
    ) -> None:
        response = await self.fetch_async(f'/v0/pipes/{pipe_name}?token={self.admin_token}', method='GET')
        pipe_info = json.loads(response.body)
        pipe_endpoint_name = [node['name'] for node in pipe_info['nodes'] if pipe_info['endpoint'] == node['id'] or pipe_info['endpoint'] == node['name']][0]
        self.assertEqual(pipe_endpoint_name, expected_endpoint_name)

    async def _create_extra_workspace(self) -> Tuple[str, str]:
        workspace_to_create = f"whatever_{uuid.uuid4().hex}"
        output = await self._tb(["workspace", "create", "--user_token", self.user_token, workspace_to_create])
        self._assert_feedback_output([
            workspace_to_create,
            "created"
        ], output)
        extra_workspace = Users.get_by_name(workspace_to_create)
        self.workspaces_to_delete.append(extra_workspace)

        token_extra_workspace = Users.get_token_for_scope(extra_workspace, scopes.ADMIN_USER)

        return workspace_to_create, token_extra_workspace


class TestCLIAuth(TestCLI):
    def setUp(self) -> None:
        super().setUp()

        self.MULTI_REGIONS = {
            'regions': [{
                'name': 'host_1_name',
                'host': self.host,
                'api_host': self.api_host,
                'key': 'host_1_name',
                'priority': 1
            }, {
                'name': 'host_2_name',
                'host': self.host,
                'api_host': self.api_host,
                'key': 'host_2_name',
                'priority': 2
            }]
        }

        # Alternative region list, to test cases where one of them has
        # connectivity issues and/or the host doesn't accept a given token
        self.MULTI_REGIONS_ALT = {
            'regions': [{
                'name': 'host_1_name',
                'host': 'https://tb-ui.example.com',
                'api_host': 'https://tb-api.example.com',
                'key': 'host_1_name',
                'priority': 1
            }, {
                'name': 'host_2_name',
                'host': self.host,
                'api_host': self.host,
                'key': 'host_2_name',
                'priority': 2
            }]
        }

    @tornado.testing.gen_test
    async def test_cli_should_alert_if_ignoring_ssl_checks(self) -> None:
        expected = self._clean_output(FeedbackManager.warning_disabled_ssl_checks())

        output = await self._tb(["auth", f'--host={self.host}'], input='WRONG_TOKEN', assert_exit_code=1)
        self.assertNotIn(expected, output)

        os.environ['TB_DISABLE_SSL_CHECKS'] = 'true'
        output = await self._tb(["auth", f'--host={self.host}'], input='WRONG_TOKEN', assert_exit_code=1)
        self.assertIn(expected, output)

        del os.environ['TB_DISABLE_SSL_CHECKS']

    @tornado.testing.gen_test
    async def test_auth__should_return_an_error_if_token_is_wrong(self) -> None:
        output = await self._tb(["auth", f'--host={self.host}'], input='WRONG_TOKEN', assert_exit_code=1)
        expected = self._clean_output(FeedbackManager.error_invalid_token())

        self.assertTrue(expected in output)

    @tornado.testing.gen_test
    async def test_auth__should_work_if_token_is_correct(self) -> None:
        output = await self._tb(["auth", f'--host={self.host}'], input=self.admin_token, assert_exit_code=0)
        expected = [FeedbackManager.success_auth(),
                    FeedbackManager.success_remember_api_host(api_host=self.host)]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_auth__should_work_in_any_host_if_token_is_correct(self) -> None:
        with patch.object(TinyB, 'regions', return_value=self.MULTI_REGIONS_ALT):
            output = await self._tb(["auth", '--host=https://tb-api.example.com'], input=f'{self.admin_token}', assert_exit_code=0)
        expected = [FeedbackManager.success_auth(),
                    FeedbackManager.success_using_host(host=self.host, name='host_2_name'),
                    FeedbackManager.success_remember_api_host(api_host=self.host)]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_auth__should_let_you_chose_the_first_host(self) -> None:
        with patch.object(TinyB, 'regions', return_value=self.MULTI_REGIONS):
            output = await self._tb(["auth", "--interactive"], input=f'1\n{self.admin_token}', assert_exit_code=0)

        expected = [
            FeedbackManager.info_available_regions(),
            'host_1_name',
            self.host,
            FeedbackManager.success_auth()
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_auth__should_let_you_chose_the_second_host(self) -> None:
        with patch.object(TinyB, 'regions', return_value=self.MULTI_REGIONS):
            output = await self._tb(["auth", "--interactive"], input=f'2\n{self.admin_token}', assert_exit_code=0)

        expected = [
            FeedbackManager.info_available_regions(),
            'host_2_name',
            self.host,
            FeedbackManager.success_auth()
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_auth__should_let_you_use_a_different_host(self) -> None:
        with patch.object(TinyB, 'regions', return_value=self.MULTI_REGIONS):
            await self._tb(["auth", "--interactive"], input=f'1\n{self.admin_token}')
            output = await self._tb(["auth", "use", "1"], assert_exit_code=0)

        expected = [
            self.host,
            FeedbackManager.success_auth()
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_auth__should_let_you_use_a_different_host_by_name(self) -> None:
        with patch.object(TinyB, 'regions', return_value=self.MULTI_REGIONS):
            await self._tb(["auth", "--interactive"], input=f'1\n{self.admin_token}')
            output = await self._tb(["auth", "use", "host_2_name"])

        expected = [
            self.host,
            FeedbackManager.success_auth()
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_auth__should_use_last_configured_workspace_when_switching_to_another_region(self) -> None:
        tb_api_proxy = TBApiProxyAsync(self)
        name = f"extra_workspace_{uuid.uuid4().hex}"
        self.extra_workspace = await tb_api_proxy.register_workspace(name, self.user_account)
        self.token_extra_workspace = Users.get_token_for_scope(self.extra_workspace, scopes.ADMIN_USER)
        self.token_extra_user = UserAccounts.get_token_for_scope(self.user_account, scopes.AUTH)

        with patch.object(TinyB, 'regions', return_value=self.MULTI_REGIONS):
            await self._tb(["auth", "--region", "1"], input=f'{self.admin_token}')
            await self._tb(["auth", "--region", "2"], input=f'{self.admin_token}')
            await self._tb(["auth", "use", "1"])
            await self._tb(["workspace", "use", name])
            await self._tb(["auth", "use", "2"])
            await self._tb(["auth", "use", "1"])
            output = await self._tb(["workspace", "current"], assert_exit_code=0)

        expected = [
            name
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_auth_to_the_same_region(self) -> None:

        with patch.object(TinyB, 'regions', return_value=self.MULTI_REGIONS):
            output = await self._tb(["auth", "--host", self.host], input=f'{self.admin_token}', assert_exit_code=0)

            expected = [
                self.host,
                FeedbackManager.success_auth()
            ]
            self._assert_feedback_output(expected, output)

            output = await self._tb(["auth", "ls"], assert_exit_code=0)

            default_regions = [region['name'] for region in self.MULTI_REGIONS['regions']]
            expected = list(set(default_regions + [FeedbackManager.info_available_regions()]))
            self._assert_feedback_output(expected, output)

            output = await self._tb(["auth", "-i"], input='1\n')
            expected = [
                self.host,
                FeedbackManager.success_auth()
            ]

            self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_auth_with_token_as_parameter(self) -> None:
        # tb --token <token> auth
        output = await self._tb(['--token', self.admin_token, "auth", '--host', self.host], assert_exit_code=0)
        expected = self._clean_output(FeedbackManager.success_auth())

        # tb auth --token <token>
        output = await self._tb(["auth", '--token', self.admin_token, '--host', self.host], assert_exit_code=0)
        expected = self._clean_output(FeedbackManager.success_auth())

        self.assertTrue(expected in output)

    @tornado.testing.gen_test
    async def test_auth_ls(self) -> None:

        with patch.object(TinyB, 'regions', return_value=self.MULTI_REGIONS):
            output = await self._tb(["auth", "ls"])
            columns = ['idx', 'region', 'host', 'api', 'current']
            default_regions = [region['name'] for region in self.MULTI_REGIONS['regions']]
            ui_host = [region['host'] for region in self.MULTI_REGIONS['regions']]
            api_host = [region['api_host'] for region in self.MULTI_REGIONS['regions']]
            expected = list(set(default_regions + columns + ui_host + api_host + [FeedbackManager.info_available_regions()]))
            self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_auth__should_work_even_if_we_pass_full_url(self) -> None:
        output = await self._tb(["auth", f'--host={self.host}/v0/pipes'], input=self.admin_token)
        expected = self._clean_output(FeedbackManager.success_auth())

        self.assertTrue(expected in output)


class TestCLICheck(TestCLI):
    @tornado.testing.gen_test
    async def test_check__should_fail_if_filename_is_invalid(self) -> None:
        await self._auth()

        file = self._get_resource_path('test_wrong.datasource')
        output = await self._tb(["check", file], assert_exit_code=2)
        expected = f"Path '{file}' does not exist"  # custom Click expected
        self.assertTrue(expected in output)

    @tornado.testing.gen_test
    async def test_check__should_fail_if_data_source_is_wrong(self) -> None:
        await self._auth()

        file = self._get_resource_path('test_ds_a_bad.datasource')
        output = await self._tb(["check", file], assert_exit_code=1)
        expected = self._clean_output(FeedbackManager.error_parsing_file(filename=file, lineno=5, error=''))
        self.assertTrue(expected in output)

    @tornado.testing.gen_test
    async def test_check__should_fail_if_jsonpath_data_source_is_wrong(self) -> None:
        await self._auth()

        file = self._get_resource_path('test_ds_a_bad_jsonpath.datasource')
        output = await self._tb(["check", file], assert_exit_code=1)
        expected = self._clean_output(FeedbackManager.error_parsing_file(filename=file, lineno=5, error=''))
        self.assertTrue(expected in output)

        file = self._get_resource_path('test_ds_a_bad_jsonpath2.datasource')
        output = await self._tb(["check", file], assert_exit_code=1)
        expected = self._clean_output(FeedbackManager.error_parsing_file(filename=file, lineno=5, error=''))
        self.assertTrue(expected in output)

    @tornado.testing.gen_test
    async def test_check__should_work_if_data_source_is_correct(self) -> None:
        await self._auth()

        file = self._get_resource_path('test_ds_a_good.datasource')
        output = await self._tb(["check", file])
        expected = self._clean_output(FeedbackManager.success_processing_file(filename=file))

        self.assertTrue(expected in output)

    @tornado.testing.gen_test
    async def test_check__should_work_if_jsonpath_data_source_is_correct(self) -> None:
        await self._auth()

        file = self._get_resource_path('test_ds_a_good_jsonpath.datasource')
        output = await self._tb(["check", file])
        expected = self._clean_output(FeedbackManager.success_processing_file(filename=file))

        self.assertTrue(expected in output)

    @tornado.testing.gen_test
    async def test_check__should_work_with_engine_settings(self) -> None:
        await self._auth()

        file = self._get_resource_path('test_ds_engine_settings.datasource')

        output = await self._tb(["check", file])
        expected = self._clean_output(FeedbackManager.success_processing_file(filename=file))

        self.assertTrue(expected in output)

    @tornado.testing.gen_test
    async def test_check__should_work_with_engine_ttl(self) -> None:
        await self._auth()

        file = self._get_resource_path('test_ds_engine_ttl.datasource')
        output = await self._tb(["check", file])
        expected = self._clean_output(FeedbackManager.success_processing_file(filename=file))

        self.assertTrue(expected in output)

    @tornado.testing.gen_test
    async def test_check__should_fail_if_pipe_is_wrong(self) -> None:
        await self._auth()

        file = self._get_resource_path('test_pipe_a_bad.pipe')
        output = await self._tb(["check", file], assert_exit_code=1)
        expected = self._clean_output(FeedbackManager.error_parsing_file(filename=file, lineno=3, error=''))
        self.assertTrue(expected in output)

    @tornado.testing.gen_test
    async def test_check__should_fail_if_pipe_sql_is_wrong(self) -> None:
        await self._auth()

        file = self._get_resource_path('test_pipe_a_bad_sql_syntax.pipe')
        output = await self._tb(["check", file], assert_exit_code=1)
        expected = self._clean_output(FeedbackManager.error_parsing_file(filename=file, lineno='', error='DB::Exception: Syntax error: failed at position'))
        self.assertTrue(expected in output)

    @tornado.testing.gen_test
    async def test_check__should_work_if_pipe_is_correct(self) -> None:
        await self._auth()

        file = self._get_resource_path('test_pipe_a_good.pipe')
        output = await self._tb(["check", file])
        expected = self._clean_output(FeedbackManager.success_processing_file(filename=file))

        self.assertTrue(expected in output)

    @tornado.testing.gen_test
    async def test_check__should_work_if_pipe_materialized(self) -> None:
        await self._auth()

        file = self._get_resource_path('test_pipe_populate.pipe')
        output = await self._tb(["check", file])
        expected = self._clean_output(FeedbackManager.success_processing_file(filename=file))

        self.assertTrue(expected in output)

        file = self._get_resource_path('test_pipe_populate2.pipe')
        output = await self._tb(["check", file])
        expected = self._clean_output(FeedbackManager.success_processing_file(filename=file))

        self.assertTrue(expected in output)

    @tornado.testing.gen_test
    async def test_check_pipe_with_unclosed_if(self) -> None:
        await self._auth()

        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe')
        pipe_file.write("""
VERSION 0

NODE mt
SQL >
    %
    SELECT
        {% if defined(x) %}
            x,
        1""")
        pipe_file.seek(0)
        output = await self._tb(["check", pipe_file.name], assert_exit_code=1)
        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file.name),
            FeedbackManager.error_parsing_node_with_unclosed_if(
                node="mt",
                pipe=pipe_file.name,
                sql="\n    SELECT\n        {% if defined(x) %}\n            x,\n        1",
                lineno=3
            )
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_check_pipe_with_unclosed_if_in_included_file(self) -> None:
        await self._auth()

        (include_file, _) = self.create_tmp_file(suffix='.incl.pipe')
        include_file.write("""
NODE included_node
SQL >
    %
    SELECT
        {% if defined(x) %}
            x,
        1
""")
        include_file.seek(0)

        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe')
        pipe_file.write(f"""
VERSION 0

INCLUDE "{include_file.name}"

NODE mt
SQL >
    SELECT * FROM included_node

""")
        pipe_file.seek(0)
        output = await self._tb(["check", pipe_file.name], assert_exit_code=1)
        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file.name),
            FeedbackManager.error_parsing_node_with_unclosed_if(
                node="included_node",
                pipe=pipe_file.name,
                sql="\n    SELECT\n        {% if defined(x) %}\n            x,\n        1",
                lineno=3

            )
        ]

        self._assert_feedback_output(expected, output)


class TestCLIToken(TestCLI):
    @tornado.testing.gen_test
    async def test_token_should_return_an_error_if_no_token(self) -> None:
        result = await self.runner.invoke(self.tb, ["pipe", "ls"])
        self.assertTrue(isinstance(result.exception, AuthNoTokenException))

    @tornado.testing.gen_test
    async def test_token_should_return_an_error_if_token_is_wrong(self) -> None:
        result = await self.runner.invoke(self.tb, ["--token", "BAD_TOKEN", "pipe", "ls"])
        self.assertFalse(isinstance(result.exception, AuthNoTokenException))
        self.assertTrue(isinstance(result.exception, AuthException))

    @tornado.testing.gen_test
    async def test_token_should_be_overriden_by_envvar(self) -> None:
        # Save .tinyb file
        await self._tb(["auth", f'--host={self.host}'], input=f'{self.admin_token}')

        # Check .tinyb file is overriden by envvar
        output = await self._tb([f'--host={self.host}',
                                 "pipe", "ls"],
                                env={'TB_TOKEN': self.admin_token})
        self.assertTrue("test_pipe" in output)

    @tornado.testing.gen_test
    async def test_token_should_be_overriden_by_flag(self) -> None:
        output = await self._tb([f'--token={self.admin_token}',
                                 f'--host={self.host}',
                                 "pipe", "ls"],
                                env={'TB_TOKEN': "BAD_TOKEN"})
        self.assertTrue("test_pipe" in output)


class TestCLIDependencies(TestCLI):
    @tornado.testing.gen_test
    async def test_dependencies__should_print_dependencies_correctly(self) -> None:
        await self._auth()

        output = await self._tb(["dependencies"])
        expected = '** test_table** --- test_pipe'
        self.assertTrue(expected in output)

    @tornado.testing.gen_test
    async def test_dependencies__filters_correctly_per_datasources(self) -> None:
        await self._auth()

        await self._tb(["push", self._get_resource_path('dependencies/ds1.datasource')])
        await self._tb(["push", self._get_resource_path('dependencies/ds2.datasource')])
        await self._tb(["push", self._get_resource_path('dependencies/mv1to2.pipe')])
        await self._tb(["push", self._get_resource_path('dependencies/ds3.datasource')])
        await self._tb(["push", self._get_resource_path('dependencies/mv2to3.pipe')])

        output = await self._tb(["dependencies", "--datasource", "ds1"])
        expected = [
            FeedbackManager.info_dependency_list(dependency='ds1'),
            FeedbackManager.info_dependency_list_item(dependency='mv1to2'),
        ]
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_dependencies__should_print_partial_replace_dependencies_correctly(self) -> None:
        await self._auth()

        await self._tb(["push", self._get_resource_path('dependencies/ds1.datasource')])
        await self._tb(["push", self._get_resource_path('dependencies/ds2.datasource')])
        await self._tb(["push", self._get_resource_path('dependencies/mv1to2.pipe')])
        await self._tb(["push", self._get_resource_path('dependencies/ds3.datasource')])
        await self._tb(["push", self._get_resource_path('dependencies/mv2to3.pipe')])

        output = await self._tb(["dependencies", "--datasource", "ds1", "--check-for-partial-replace"], assert_exit_code=1)
        expected = [
            FeedbackManager.info_dependency_list(dependency='ds2'),
            FeedbackManager.info_dependency_list_item(dependency='mv1to2'),
            FeedbackManager.info_no_compatible_dependencies_found(),
            FeedbackManager.info_dependency_list(dependency='ds3'),
            FeedbackManager.error_partial_replace_cant_be_executed(datasource='ds1')
        ]
        self._assert_feedback_output(expected, output)


class TestCLIInit(TestCLI):
    @tornado.testing.gen_test
    async def test_init__should_initialize_directory_correctly(self) -> None:
        await self._auth()

        output = await self._tb(["init", f'--folder={self.CLI_PROJECT_PATH}'])
        expected = [FeedbackManager.info_path_created(path=path) for path in PROJECT_PATHS]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_init__should_show_message_when_path_already_exists(self) -> None:
        await self._auth()

        output = await self._tb(["init", f'--folder={self.CLI_PROJECT_PATH}'])
        output = await self._tb(["init", f'--folder={self.CLI_PROJECT_PATH}'])
        expected = [FeedbackManager.info_path_already_exists(path=path) for path in PROJECT_PATHS]
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_init__should_initialize_with_files(self) -> None:
        await self._auth()

        output = await self._tb(["init", f'--folder={self.CLI_PROJECT_PATH}fixtures', '--generate-datasources'])
        expected = [FeedbackManager.info_path_created(path=path) for path in PROJECT_PATHS]
        self._assert_feedback_output(expected, output)

        for format in SUPPORTED_FORMATS:
            for filename in glob.glob(f'{os.path.dirname(__file__)}/cli/fixtures/*.{format}'):
                filename = filename.split('/')[-1]
                stem = filename.split(".")[0]
                expected = FeedbackManager.success_generated_file(file=f'{stem}.datasource', stem=stem, filename=f'{self.CLI_PROJECT_PATH}fixtures/{filename}')
                self.assertTrue(self._clean_output(expected) in output)

                # Generating fixtures for Parquet is not supported
                if format != 'parquet':
                    expected = FeedbackManager.success_generated_fixture(fixture=f'fixtures/{filename}')
                    self.assertTrue(self._clean_output(expected) in output)
                else:
                    self.assertTrue(self._clean_output(FeedbackManager.warning_parquet_fixtures_not_supported()) in output)

                with open(f'{self.CLI_PROJECT_PATH}{stem}.datasource') as f:
                    assert schema_expectations[stem] in ''.join(f.readlines())

    @tornado.testing.gen_test
    async def test_init__should_initialize_with_files_force(self) -> None:
        await self._auth()

        await self._tb(["init", f'--folder={self.CLI_PROJECT_PATH}fixtures', '--generate-datasources'])
        output = await self._tb(["init", f'--folder={self.CLI_PROJECT_PATH}fixtures', '--generate-datasources', '--force'])

        expected = [FeedbackManager.info_path_created(path=path) for path in PROJECT_PATHS]
        self._assert_feedback_output(expected, output, not_in=True)

        for format in SUPPORTED_FORMATS:
            for filename in glob.glob(f'{os.path.dirname(__file__)}/cli/fixtures/*.{format}'):
                filename = filename.split('/')[-1]
                stem = filename.split(".")[0]
                expected = FeedbackManager.success_generated_file(file=f'{stem}.datasource', stem=stem, filename=f'{self.CLI_PROJECT_PATH}fixtures/{filename}')
                self.assertTrue(self._clean_output(expected) in output)

                # Generating fixtures for Parquet is not supported
                if format != 'parquet':
                    expected = FeedbackManager.success_generated_fixture(fixture=f'fixtures/{filename}')
                    self.assertTrue(self._clean_output(expected) in output)
                else:
                    self.assertTrue(self._clean_output(FeedbackManager.warning_parquet_fixtures_not_supported()) in output)

                with open(f'{self.CLI_PROJECT_PATH}{stem}.datasource') as f:
                    assert schema_expectations[stem] in ''.join(f.readlines())

    @tornado.testing.gen_test
    async def test_init__should_initialize_with_files_force_false(self) -> None:
        await self._auth()

        await self._tb(["init", f'--folder={self.CLI_PROJECT_PATH}fixtures', '--generate-datasources'])
        output = await self._tb(["init", f'--folder={self.CLI_PROJECT_PATH}fixtures', '--generate-datasources'])

        expected = [FeedbackManager.info_path_already_exists(path=path) for path in PROJECT_PATHS]
        self._assert_feedback_output(expected, output)

        for format in SUPPORTED_FORMATS:
            for filename in glob.glob(f'{os.path.dirname(__file__)}/cli/fixtures/*.{format}'):
                filename = filename.split('/')[-1]
                stem = filename.split(".")[0]
                expected = FeedbackManager.error_file_already_exists(file=f'{stem}.datasource')
                self.assertTrue(self._clean_output(expected) in output)

                with open(f'{self.CLI_PROJECT_PATH}{stem}.datasource') as f:
                    assert schema_expectations[stem] in ''.join(f.readlines())


class TestCLIPush(TestCLI):
    @tornado.testing.gen_test
    async def test_push__should_push_data_source_correctly(self) -> None:
        await self._auth()

        name = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file])

        expected = [
            FeedbackManager.info_processing_file(filename=file),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=name, version=''),
            FeedbackManager.success_create(name=name),
            FeedbackManager.info_not_pushing_fixtures()
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_push__duplicated_column(self) -> None:
        await self._auth()
        with tempfile.NamedTemporaryFile(suffix=".datasource", mode='w+', encoding='utf-8') as datasource_file:
            datasource_file.write("""
SCHEMA >
    `a1` Int64,
    `a1` String

ENGINE "MergeTree"
            """)
            datasource_file.seek(0)
            output = await self._tb(["push", datasource_file.name], assert_exit_code=1)

            expected = [
                "Failed creating Data Source: Duplicated column in schema: 'a1'"
            ]

            self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_push__should_not_push_with_fixtures_if_there_is_data(self) -> None:
        name = 'sales'

        await self._auth()
        await self._tb(["datasource", "truncate", name, "--yes"],
                       assert_exit_code=1)

        file = self._get_resource_path(f'{name}.datasource')

        output = await self._tb(["push", file, '--fixtures'])
        expected = [FeedbackManager.info_pushing_fixtures()]
        self._assert_feedback_output(expected, output)

        output = await self._tb(["push", file, '--fixtures'],
                                assert_exit_code=1)
        expected = [FeedbackManager.error_push_fixture_will_replace_data(datasource=name)]
        self._assert_feedback_output(expected, output)

        output = await self._tb(["push", file, '--fixtures', '--force'])
        expected = [FeedbackManager.info_pushing_fixtures()]
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_push__should_prompt_version_if_called_with_dry_run(self) -> None:
        await self._auth()

        name = 'test_ds_a_good_with_version'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file, "--dry-run"])

        expected = [
            FeedbackManager.info_processing_file(filename=file),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_dry_processing_new_resource(name=name, version='(v1)')
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_push__should_prompt_version_if_called_with_dry_run_and_force(self) -> None:
        await self._auth()

        name = 'test_ds_a_good_with_version'
        file = self._get_resource_path(f'{name}.datasource')
        await self._tb(["push", file])
        second_output = await self._tb(["push", file, "--force", "--dry-run"])

        expected = [
            FeedbackManager.info_processing_file(filename=file),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_dry_processing_resource(name=name, version='1', latest_version='1'),
        ]

        self._assert_feedback_output(expected, second_output)

    @tornado.testing.gen_test
    async def test_push__should_push_ndjson_data_source_correctly(self) -> None:
        await self._auth()

        name = 'test_ds_a_good_jsonpath'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file])

        expected = [
            FeedbackManager.info_processing_file(filename=file),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=name, version=''),
            FeedbackManager.success_create(name=name),
            FeedbackManager.info_not_pushing_fixtures()
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_push__should_push_data_source_with_engine_settings(self) -> None:
        await self._auth()

        names = ['test_ds_engine_settings', 'test_ds_engine_settings_am']

        for name in names:
            file = self._get_resource_path(f'{name}.datasource')
            output = await self._tb(["push", file])

            expected = [
                FeedbackManager.info_processing_file(filename=file),
                FeedbackManager.info_building_dependencies(),
                FeedbackManager.info_processing_new_resource(name=name, version=''),
                FeedbackManager.success_create(name=name),
                FeedbackManager.info_not_pushing_fixtures()
            ]

            self._assert_feedback_output(expected, output)

            file = f'{self.CLI_PROJECT_PATH}{name}.datasource'
            output = await self._tb(["pull", f"--match={name}", f'--folder={self.CLI_PROJECT_PATH}'])

            expected = [
                FeedbackManager.info_writing_resource(resource=file, prefix='')
            ]

            found = False
            with open(file, "r") as downloaded_file:
                for line in downloaded_file:
                    if 'SETTINGS' in line:
                        self.assertTrue("index_granularity = 32" in line)
                        found = True
                        break

            self.assertTrue(found)

            self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_push__should_push_data_source_with_engine_ttl(self) -> None:
        await self._auth()

        name = 'test_ds_engine_ttl'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file])

        expected = [
            FeedbackManager.info_processing_file(filename=file),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=name, version=''),
            FeedbackManager.success_create(name=name),
            FeedbackManager.info_not_pushing_fixtures()
        ]

        self._assert_feedback_output(expected, output)

        file = f'{self.CLI_PROJECT_PATH}{name}.datasource'
        output = await self._tb(["pull", f"--match={name}", f'--folder={self.CLI_PROJECT_PATH}'])
        expected = [
            FeedbackManager.info_writing_resource(resource=file, prefix='')
        ]

        found = False
        with open(file, "r") as downloaded_file:
            for line in downloaded_file:
                if 'TTL' in line:
                    self.assertTrue("toDate(a1) + toIntervalDay(1)" in line)
                    found = True
                    break

        self.assertTrue(found)

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_push__should_not_push_pipe_with_wrong_resources(self) -> None:
        await self._auth()

        name = 'test_pipe_a_good'
        datasource = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", file], assert_exit_code=1)

        expected = [
            FeedbackManager.info_processing_file(filename=file),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=name, version=''),
            FeedbackManager.error_push_file_exception(filename=file, error=''),
            FeedbackManager.error_pushing_pipe(pipe=name, error=f"Resource '{datasource}' not found")
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_push__should_push_pipe_correctly(self) -> None:
        await self._auth()

        name = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file])

        name = 'test_pipe_a_good'
        file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", file])

        expected = [
            FeedbackManager.info_processing_file(filename=file),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=name, version=''),
            FeedbackManager.success_create(name=name),
            FeedbackManager.info_not_pushing_fixtures()
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_should_not_push_pipe_with_missing_sql(self) -> None:
        await self._auth()

        name = 'test_pipe_missing_sql'
        file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", file], assert_exit_code=1)
        print(f"output: {output}")
        expected = [
            FeedbackManager.error_missing_sql_command()
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_should_not_push_pipe_with_missing_node_name(self) -> None:
        await self._auth()

        name = 'test_pipe_missing_node_name'
        file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", file], assert_exit_code=1)

        expected = [
            FeedbackManager.error_missing_node_name()
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_should_not_push_pipe_with_missing_datasource_name(self) -> None:
        await self._auth()

        name = 'test_pipe_missing_datasource'
        file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", file], assert_exit_code=1)

        expected = [
            FeedbackManager.error_missing_datasource_name()
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_push_should_not_push_pipe_with_dashes(self) -> None:
        await self._auth()
        name = 'test_pipe_starting_with_dash'
        file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", file], assert_exit_code=1)
        expected = [
            FeedbackManager.info_processing_file(filename=file),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=name, version=''),
            FeedbackManager.error_push_file_exception(filename=file, error=''),
            FeedbackManager.error_pushing_pipe(pipe=name, error='Invalid node name "-mv". Name must start with a letter and contain only letters, numbers, and underscores. Hint: use mv_')
        ]
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_push__should_create_copy_pipe_correctly(self) -> None:
        with User.transaction(self.WORKSPACE_ID) as w:
            w.feature_flags[FeatureFlagWorkspaces.EXPORT.value] = True
            self.workspace = w
        await self._auth()

        origin_ds_name = 'test_ds_a_good'
        origin_ds_file = self._get_resource_path(f'{origin_ds_name}.datasource')
        await self._tb(["push", origin_ds_file])

        target_ds_name = 'test_ds_a_good_with_description'
        target_ds_file = self._get_resource_path(f'{target_ds_name}.datasource')
        await self._tb(["push", target_ds_file])

        pipe_name = 'test_pipe_copy'
        pipe_file = self._get_resource_path(f'{pipe_name}.pipe')
        output = await self._tb(["push", pipe_file])

        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=pipe_name, version=''),
        ]

        with User.transaction(self.WORKSPACE_ID) as w:
            w.feature_flags[FeatureFlagWorkspaces.EXPORT.value] = False

        self._assert_feedback_output(expected, output)

        params = {'token': self.admin_token}

        response = await self.fetch_async(
            path=f'/v0/pipes/{pipe_name}?{urlencode(params)}',
            method='GET')
        self.assertEqual(response.code, 200)
        pipe = json.loads(response.body)
        self.assertEqual(pipe['type'], 'copy')

    @tornado.testing.gen_test
    async def test_push_force__should_update_copy_pipe(self) -> None:
        with User.transaction(self.WORKSPACE_ID) as w:
            w.feature_flags[FeatureFlagWorkspaces.EXPORT.value] = True
            self.workspace = w
        await self._auth()

        origin_ds_name = 'test_ds_a_good'
        origin_ds_file = self._get_resource_path(f'{origin_ds_name}.datasource')
        await self._tb(["push", origin_ds_file])

        target_ds_name = 'test_ds_a_good_with_description'
        target_ds_file = self._get_resource_path(f'{target_ds_name}.datasource')
        await self._tb(["push", target_ds_file])

        new_target_ds_name = 'test_ds_a_good_add_column'
        new_target_ds_file = self._get_resource_path(f'{new_target_ds_name}.datasource')
        await self._tb(["push", new_target_ds_file])

        pipe_name = 'test_pipe_copy'
        pipe_file = self._get_resource_path(f'{pipe_name}.pipe')
        await self._tb(["push", pipe_file])

        new_pipe_name = 'test_pipe_copy_target_datasource'
        new_pipe_file = self._get_resource_path(f'{new_pipe_name}.pipe')
        params = {'token': self.admin_token, 'name': new_pipe_name}
        response = await self.fetch_async(
            path=f'/v0/pipes/{pipe_name}?{urlencode(params)}',
            method='PUT',
            body='')

        output = await self._tb(["push", new_pipe_file, "--force"])

        expected = [
            FeedbackManager.info_processing_file(filename=new_pipe_file),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=new_pipe_name, version=''),
        ]

        self._assert_feedback_output(expected, output)

        params = {'token': self.admin_token}

        response = await self.fetch_async(
            path=f'/v0/pipes/{new_pipe_name}?{urlencode(params)}',
            method='GET')

        pipe = json.loads(response.body)
        target_datasource_id = pipe['copy_target_datasource']

        response = await self.fetch_async(
            path=f'/v0/datasources/{target_datasource_id}?{urlencode(params)}',
            method='GET')
        target_datasource = json.loads(response.body)

        self.assertEqual(pipe['name'], new_pipe_name)
        self.assertEqual(pipe['type'], 'copy')
        self.assertEqual(target_datasource["name"], new_target_ds_name)

        with User.transaction(self.WORKSPACE_ID) as w:
            w.feature_flags[FeatureFlagWorkspaces.EXPORT.value] = False

    @tornado.testing.gen_test
    async def test_push__should_push_pipe_correctly_with_encoding(self) -> None:
        await self._auth()

        name = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file])

        name = 'test_pipe_a_good_encoding'
        file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", file])

        expected = [
            FeedbackManager.info_processing_file(filename=file),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=name, version=''),
            FeedbackManager.success_create(name=name),
            FeedbackManager.info_not_pushing_fixtures()
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test__push__should_push_endpoint_and_create_read_token(self) -> None:
        await self._auth()

        name = 'test_endpoint_with_read_token'
        file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", file])
        expected = [
            FeedbackManager.info_processing_file(filename=file),
            FeedbackManager.info_create_not_found_token(token='test_read_token'),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=name, version=''),
            FeedbackManager.success_create(name=name),
            FeedbackManager.info_not_pushing_fixtures()
        ]

        self._assert_feedback_output(expected, output)

        output = await self._tb(["push", file, '--force'])
        expected = [
            FeedbackManager.info_processing_file(filename=file),
            FeedbackManager.info_create_found_token(token='test_read_token'),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=name, version=''),
            FeedbackManager.success_create(name=name),
            FeedbackManager.info_not_pushing_fixtures()
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test__push__should_push_endpoint_and_hide_token(self) -> None:
        await self._auth()

        expected = ["p.ey****...****"]

        name = 'test_endpoint_with_read_token'
        file = self._get_resource_path(f'{name}.pipe')

        # Hidden
        output = await self._tb(['--hide-tokens', "push", file, '--force'])
        self._assert_feedback_output(expected, output)

        # Visible
        output = await self._tb(["push", file, '--force'])
        self._assert_feedback_output(expected, output, not_in=True)

    @tornado.testing.gen_test
    async def test_push__should_push_pipe_escaped_quote_correctly(self) -> None:
        await self._auth()

        name = 'test_quote_pipe'
        file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", file])

        expected = [
            FeedbackManager.info_processing_file(filename=file),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=name, version=''),
            FeedbackManager.success_create(name=name),
            FeedbackManager.info_not_pushing_fixtures()
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_push__should_not_push_data_source_with_wrong_agg_functions(self) -> None:
        await self._auth()

        name = 'test_wrong_agg_functions'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file], assert_exit_code=1)

        matview_error = 'Invalid data source structure'

        expected = [
            matview_error
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_push__cli_skips_datasource_if_already_exists(self) -> None:
        await self._auth()

        name = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.datasource')
        await self._tb(["push", file])
        second_output = await self._tb(["push", file])

        expected = [
            FeedbackManager.warning_name_already_exists(name=name)
        ]

        self._assert_feedback_output(expected, second_output)

    @tornado.testing.gen_test
    async def test_push__cli_skips_datasource_with_versions_if_already_exists(self) -> None:
        await self._auth()

        name = 'videos'
        file = self._get_resource_path(f'{name}.datasource')
        await self._tb(["push", file])
        second_output = await self._tb(["push", file])

        expected = [
            FeedbackManager.warning_name_already_exists(name=f"{name}__v1")
        ]

        self._assert_feedback_output(expected, second_output)

    @tornado.testing.gen_test
    async def test__push__should_push_datasource_and_create_append_token(self) -> None:
        await self._auth()

        name = 'test_ds_a_good_with_token'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file])
        expected = [
            FeedbackManager.info_processing_file(filename=file),
            FeedbackManager.info_create_not_found_token(token='test_append_token'),
            FeedbackManager.success_create(name=name),
            FeedbackManager.info_not_pushing_fixtures()
        ]

        self._assert_feedback_output(expected, output)
        output = await self._tb(["datasource", "rm", "test_ds_a_good_with_token", "--yes"])

        output = await self._tb(["push", file])
        expected = [
            FeedbackManager.info_processing_file(filename=file),
            FeedbackManager.info_create_found_token(token='test_append_token'),
            FeedbackManager.success_create(name=name),
            FeedbackManager.info_not_pushing_fixtures()
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_push__cli_tries_to_replace_datasource_if_called_with_force(self) -> None:
        await self._auth()

        name = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.datasource')
        await self._tb(["push", file])
        second_output = await self._tb(["push", file, "--force"])

        expected = [
            FeedbackManager.info_processing_new_resource(name=name, version=''),
            FeedbackManager.warning_datasource_already_exists(datasource=name),
        ]

        self._assert_feedback_output(expected, second_output)

    @tornado.testing.gen_test
    async def test_push__cli_replaces_datasource_if_called_with_force_and_the_envar_is_set(self) -> None:
        await self._auth()

        name = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.datasource')
        await self._tb(["push", file])

        second_output = await self._tb(["push", file, "--force"], input=name, env={'TB_I_KNOW_WHAT_I_AM_DOING': "true"})

        expected = [
            FeedbackManager.info_processing_new_resource(name=name, version=''),
            FeedbackManager.info_ask_for_datasource_confirmation(),
            FeedbackManager.success_delete_datasource(datasource=name)
        ]

        self._assert_feedback_output(expected, second_output)

    async def _push_new_datasource_will_offer_the_alter_operation(
        self,
        first_name: str,
        second_name: str,
        check_text: Optional[str] = None,
        user_cancels: bool = False,
        assert_exit_code: int = 0
    ) -> None:
        await self._auth()

        file = self._get_resource_path(f'{first_name}.datasource')
        await self._tb(["push", file])

        rename_first_datasource_to_match_the_second_file = await self.http_client.fetch(
            self.get_url(f"/v0/datasources/{first_name}?{urlencode({'name': second_name, 'token': self.admin_token})}"),
            method='PUT', body=''
        )

        self.assertEqual(rename_first_datasource_to_match_the_second_file.code, 200)

        second_file = self._get_resource_path(f'{second_name}.datasource')
        second_output = await self._tb(["push", second_file, "--force"], input="y" if not user_cancels else "n",
                                       assert_exit_code=assert_exit_code)

        expected = [
            FeedbackManager.info_processing_new_resource(name=second_name, version=''),
            FeedbackManager.info_datasource_doesnt_match(datasource=second_name),
            FeedbackManager.info_ask_for_alter_confirmation(),
        ]

        if check_text:
            expected.insert(2, check_text)

        if not user_cancels:
            expected.append(FeedbackManager.success_datasource_alter())
        else:
            expected += [
                FeedbackManager.error_push_file_exception(filename=second_file, error=''),
                FeedbackManager.error_datasource_already_exists_and_alter_failed(
                    datasource=second_name, alter_error_message='Alter datasource cancelled')
            ]

        self._assert_feedback_output(expected, second_output)

    @tornado.testing.gen_test
    async def test_push__in_case_of_new_column__a_push_force_will_offer_the_alter_operation(self) -> None:
        await self._push_new_datasource_will_offer_the_alter_operation('test_ds_a_good', 'test_ds_a_good_add_column', '-  ADD COLUMN `a4` String')

    @tornado.testing.gen_test
    async def test_push__in_case_of_new_description__a_push_force_will_offer_the_alter_operation(self) -> None:
        await self._push_new_datasource_will_offer_the_alter_operation('test_ds_a_good', 'test_ds_a_good_with_description')

    @tornado.testing.gen_test
    async def test_push__in_case_of_new_ttl__a_push_force_will_offer_the_alter_operation(self) -> None:
        await self._push_new_datasource_will_offer_the_alter_operation('test_ds_engine_no_ttl', 'test_ds_engine_ttl', '-  MODIFY TTL toDate(a1) + toIntervalDay(1)')

    @tornado.testing.gen_test
    async def test_push__in_case_of_modified_ttl__a_push_force_will_offer_the_alter_operation(self) -> None:
        await self._push_new_datasource_will_offer_the_alter_operation('test_ds_engine_ttl', 'test_ds_engine_ttl_3_days', '-  MODIFY TTL toDate(a1) + toIntervalDay(3)')

    @tornado.testing.gen_test
    async def test_push__in_case_of_new_column__a_push_force_will_offer_the_alter_operation_but_user_cancels(self) -> None:
        await self._push_new_datasource_will_offer_the_alter_operation('test_ds_a_good', 'test_ds_a_good_add_column', '-  ADD COLUMN `a4` String', True,
                                                                       assert_exit_code=1)

    @tornado.testing.gen_test
    async def test_push__in_case_of_new_description__a_push_force_will_offer_the_alter_operation_but_user_cancels(self) -> None:
        await self._push_new_datasource_will_offer_the_alter_operation('test_ds_a_good', 'test_ds_a_good_with_description', None, True,
                                                                       assert_exit_code=1)

    @tornado.testing.gen_test
    async def test_push__in_case_of_new_ttl__a_push_force_will_offer_the_alter_operation_but_user_cancels(self) -> None:
        await self._push_new_datasource_will_offer_the_alter_operation('test_ds_engine_no_ttl', 'test_ds_engine_ttl', '-  MODIFY TTL toDate(a1) + toIntervalDay(1)', True,
                                                                       assert_exit_code=1)

    @tornado.testing.gen_test
    async def test_push__in_case_of_modified_ttl__a_push_force_will_offer_the_alter_operation_but_user_cancels(self) -> None:
        await self._push_new_datasource_will_offer_the_alter_operation('test_ds_engine_ttl', 'test_ds_engine_ttl_3_days', '-  MODIFY TTL toDate(a1) + toIntervalDay(3)', True,
                                                                       assert_exit_code=1)

    @tornado.testing.gen_test
    async def test_push__in_case_new_column_and_ttl_false(self) -> None:
        await self._push_new_datasource_will_offer_the_alter_operation('test_ds_engine_no_ttl', 'test_ds_engine_ttl_false_new_column', '-  ADD COLUMN `a4` String', True,
                                                                       assert_exit_code=1)

    @tornado.testing.gen_test
    async def test_push__in_case_existing_ttl_is_set_to_false(self) -> None:
        await self._push_new_datasource_will_offer_the_alter_operation('test_ds_engine_ttl_3_days', 'test_ds_engine_no_ttl', '-  REMOVE TTL', True,
                                                                       assert_exit_code=1)

    async def _push_two_files_and_check_that_second_one_is_updated(
        self,
        first_name: str,
        second_name: str,
    ) -> None:
        await self._auth()

        file = self._get_resource_path(f'{first_name}.datasource')
        await self._tb(["push", file])

        rename_first_datasource_to_match_the_second_file = await self.http_client.fetch(
            self.get_url(f"/v0/datasources/{first_name}?{urlencode({'name': second_name, 'token': self.admin_token})}"),
            method='PUT', body=''
        )

        self.assertEqual(rename_first_datasource_to_match_the_second_file.code, 200)

        second_file = self._get_resource_path(f'{second_name}.datasource')
        second_output = await self._tb(["push", second_file, "--force", "--yes"])

        expected = [
            FeedbackManager.info_processing_new_resource(name=second_name, version=''),
            FeedbackManager.info_datasource_doesnt_match(datasource=second_name),
            FeedbackManager.success_datasource_alter(),
            FeedbackManager.success_create(name=second_name)
        ]

        self._assert_feedback_output(expected, second_output)

        # Lastly, check that the pushed file matches the one that we pull to ensure the description
        # was properly updated in the backend
        downloaded_file = f'{self.CLI_PROJECT_PATH}{second_name}.datasource'
        output = await self._tb(["pull", f"--match={second_name}", f'--folder={self.CLI_PROJECT_PATH}'])
        expected = [
            FeedbackManager.info_writing_resource(resource=downloaded_file, prefix='')
        ]

        self._assert_feedback_output(expected, output)

        original_file_content = Path(second_file).read_text().strip()
        downloaded_file_content = Path(downloaded_file).read_text().strip()

        self.assertEqual(original_file_content, downloaded_file_content)

    @tornado.testing.gen_test
    async def test_push__in_case_of_new_column_and_yes_parameter__a_push_force_will_apply_the_alter_operation(self) -> None:
        await self._push_two_files_and_check_that_second_one_is_updated('test_ds_a_good', 'test_ds_a_good_add_column')

    @tornado.testing.gen_test
    async def test_push__in_case_of_new_description_and_yes_parameter__a_push_force_will_apply_the_alter_operation(self) -> None:
        await self._push_two_files_and_check_that_second_one_is_updated('test_ds_a_good', 'test_ds_a_good_with_description')

    @tornado.testing.gen_test
    async def test_push__in_case_of_new_ttl_and_yes_parameter__a_push_force_will_apply_the_alter_operation(self) -> None:
        await self._push_two_files_and_check_that_second_one_is_updated('test_ds_engine_no_ttl', 'test_ds_engine_ttl')

    @tornado.testing.gen_test
    async def test_push__in_case_of_modified_ttl_and_yes_parameter__a_push_force_will_apply_the_alter_operation(self) -> None:
        await self._push_two_files_and_check_that_second_one_is_updated('test_ds_engine_ttl', 'test_ds_engine_ttl_3_days')

    @tornado.testing.gen_test
    async def test_push__in_case_of_removing_ttl_and_yes_parameter__a_push_force_will_apply_the_alter_operation(self) -> None:
        await self._push_two_files_and_check_that_second_one_is_updated('test_ds_engine_ttl', 'test_ds_engine_ttl_removed')

    @tornado.testing.gen_test
    async def test_push__correctly_push_a_non_prefixed_resource_after_the_same_prefixed_is_pushed(self) -> None:
        await self._auth()

        datasource_name = 'test_ds_a_good'
        prefix = "r"

        file = self._get_resource_path(f'{datasource_name}.datasource')
        output_push_prefixed_datasource = await self._tb(["push", file, "--prefix", prefix])

        self._assert_feedback_output([
            FeedbackManager.success_create(name=f"{prefix}__{datasource_name}")
        ], output_push_prefixed_datasource)

        file = self._get_resource_path(f'{datasource_name}.datasource')
        output_push_non_prefixed_datasource = await self._tb(["push", file])

        self._assert_feedback_output([
            FeedbackManager.success_create(name=datasource_name)
        ], output_push_non_prefixed_datasource)

        tb_datasource_ls_output = await self._tb(["datasource", "ls"])

        self._assert_feedback_output([
            'prefix: rversion: shared from: name: test_ds_a_good',
            'prefix: version: shared from: name: test_ds_a_good',

        ], tb_datasource_ls_output)

    @tornado.testing.gen_test
    async def test_push__correctly_push_a_prefixed_resource_after_the_same_non_prefixed_is_pushed(self) -> None:
        await self._auth()

        datasource_name = 'test_ds_a_good'
        prefix = "r"

        file = self._get_resource_path(f'{datasource_name}.datasource')
        output_push_non_prefixed_datasource = await self._tb(["push", file])

        self._assert_feedback_output([
            FeedbackManager.success_create(name=datasource_name)
        ], output_push_non_prefixed_datasource)

        file = self._get_resource_path(f'{datasource_name}.datasource')
        output_push_prefixed_datasource = await self._tb(["push", file, "--prefix", prefix])

        self._assert_feedback_output([
            FeedbackManager.success_create(name=f"{prefix}__{datasource_name}")
        ], output_push_prefixed_datasource)

        tb_datasource_ls_output = await self._tb(["datasource", "ls"])

        self._assert_feedback_output([
            'prefix: rversion: shared from: name: test_ds_a_good',
            'prefix: version: shared from: name: test_ds_a_good',

        ], tb_datasource_ls_output)

    @tornado.testing.gen_test
    async def test_push__with_escaped_unicode_characters(self) -> None:
        await self._auth()

        (fp, pipe_name) = self.create_tmp_file(suffix='.pipe')

        fp.write("""
NODE mv
SQL >
  SELECT extractAll(JSONExtractString('{}', 'body'), '[😄-😇|😒-🤨|😌-😬]') emojis
""")
        # this is important to persist the file and be able to push it
        fp.close()

        second_output = await self._tb(["push", fp.name])
        expected = [
            FeedbackManager.success_create(name=pipe_name)
        ]

        self._assert_feedback_output(expected, second_output)

    @tornado.testing.gen_test
    async def test_push_a_pipe_with_a_sql_bigger_than_limit_shows_error(self) -> None:
        await self._auth()

        (fp, pipe_name) = self.create_tmp_file(suffix='.pipe')
        fp.write(f"""
NODE mv
SQL >
    SELECT '{"c" * 13 * 1024}'
            """)
        output = await self._tb(["push", fp.name], assert_exit_code=1)
        expected = [
            FeedbackManager.error_parsing_node(
                node='mv', pipe=pipe_name, error="The maximum size for a SQL query is")
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_push__custom_kafka_datasource(self) -> None:
        await self._auth()

        with patch.object(KafkaUtils, 'get_kafka_topic_group', return_value={'response': 'ok'}):
            name = 'kafka_datasource'
            file = self._get_resource_path(f'{name}.datasource')
            output = await self._tb(["push", file])

        expected = [
            FeedbackManager.info_creating_kafka_connection(connection_name='connection_name'),
            FeedbackManager.success_connection_using(connection_name='connection_name'),
            FeedbackManager.success_create(name=name)
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_push__basic_kafka_datasource(self) -> None:
        await self._auth()
        with patch.object(KafkaUtils, 'get_kafka_topic_group', return_value={'response': 'ok'}):
            (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
            datasource_file.write("""
VERSION 0

SCHEMA >
    `__value` String,
    `__topic` LowCardinality(String),
    `__partition` Int16,
    `__offset` Int64,
    `__timestamp` DateTime,
    `__key` String

ENGINE "MergeTree"
ENGINE_PARTITION_KEY "toYYYYMM(__timestamp)"
ENGINE_SORTING_KEY "__timestamp"

KAFKA_CONNECTION_NAME connection_name
KAFKA_BOOTSTRAP_SERVERS tinybird.co:80
KAFKA_KEY aaa
KAFKA_SECRET bbb
KAFKA_TOPIC ttt
KAFKA_GROUP_ID ggg
KAFKA_STORE_RAW_VALUE 'True'
""")
            datasource_file.seek(0)
            output = await self._tb(["push", datasource_file.name])

            expected = [
                FeedbackManager.info_creating_kafka_connection(connection_name='connection_name'),
                FeedbackManager.success_connection_using(connection_name='connection_name'),
                FeedbackManager.success_create(name=f"{datasource_name}__v0")
            ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_push__basic_kafka_datasource_with_ttl(self) -> None:
        await self._auth()
        with patch.object(KafkaUtils, 'get_kafka_topic_group', return_value={'response': 'ok'}):
            (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
            datasource_file.write("""
VERSION 0

SCHEMA >
    `__value` String,
    `__topic` LowCardinality(String),
    `__partition` Int16,
    `__offset` Int64,
    `__timestamp` DateTime,
    `__key` String

ENGINE "MergeTree"
ENGINE_PARTITION_KEY "toYYYYMM(__timestamp)"
ENGINE_SORTING_KEY "__timestamp"
ENGINE_TTL "toDate(__timestamp) + toIntervalDay(2)"

KAFKA_CONNECTION_NAME connection_name
KAFKA_BOOTSTRAP_SERVERS tinybird.co:80
KAFKA_KEY aaa
KAFKA_SECRET bbb
KAFKA_TOPIC ttt
KAFKA_GROUP_ID ggg
KAFKA_STORE_RAW_VALUE 'True'
""")
            datasource_file.seek(0)
            output = await self._tb(["push", datasource_file.name])
            datasource_name = f"{datasource_name}__v0"

            expected = [
                FeedbackManager.info_creating_kafka_connection(connection_name='connection_name'),
                FeedbackManager.success_connection_using(connection_name='connection_name'),
                FeedbackManager.success_create(name=datasource_name)
            ]

        self._assert_feedback_output(expected, output)

        request = await self.http_client.fetch(
            self.get_url(f"/v0/datasources/{datasource_name}?{urlencode({'token': self.admin_token})}"),
            method='GET'
        )
        self.assertEqual(request.code, 200, request.body)
        datasource_info = json.loads(request.body)

        self.assertEqual(datasource_info['engine']['ttl'], 'toDate(__timestamp) + toIntervalDay(2)', datasource_info)
        self.assertEqual(datasource_info['engine']['sorting_key'], '__timestamp', datasource_info)
        self.assertEqual(datasource_info['engine']['partition_key'], 'toYYYYMM(__timestamp)', datasource_info)

    @tornado.testing.gen_test
    async def test_push__should_not_publish_endpoint_if_materialized(self) -> None:
        await self._auth()

        pipe = 'test_pipe_populate'
        datasource = 'test_ds_a_good'
        file = self._get_resource_path(f'{datasource}.datasource')
        await self._tb(["push", file, "--force"])

        file = self._get_resource_path(f'{pipe}.pipe')
        output = await self._tb(["push", file, "--force"])
        expected = self._clean_output(FeedbackManager.success_processing_file(filename=file))

        output = await self._tb(["pipe", "data", pipe])
        expected = [
            f"The pipe '{pipe}' does not have an endpoint yet"
        ]
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_push__should_not_push_more_than_one_materialized_node(self) -> None:
        with User.transaction(self.WORKSPACE_ID) as w:
            w.feature_flags[FeatureFlagWorkspaces.PIPE_NODE_RESTRICTIONS.value] = True

        await self._auth()
        datasource = 'test_ds_a_good'
        datasource_file = self._get_resource_path(f'{datasource}.datasource')
        await self._tb(["push", datasource_file])

        pipe = 'test_pipe_bad_multiple_materialized_nodes'
        pipe_file = self._get_resource_path(f'{pipe}.pipe')
        output = await self._tb(["push", pipe_file], assert_exit_code=1)

        expected = [
            FeedbackManager.error_pushing_pipe(
                pipe=pipe,
                error="Forbidden: There is more than one materialized node. Pipes can only have one output. Set only one node to materialize and try again.")
        ]

        self._assert_feedback_output(expected, output)

        with User.transaction(self.WORKSPACE_ID) as w:
            w.feature_flags[FeatureFlagWorkspaces.PIPE_NODE_RESTRICTIONS.value] = False

    @tornado.testing.gen_test
    async def test_push__success_message_pushing_version_file(self) -> None:
        await self._auth()

        name = 'videos'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file])
        expected = [
            FeedbackManager.info_processing_file(filename=file),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=name, version='(v1)'),
            FeedbackManager.success_create(name=f"{name}__v1")
        ]
        self._assert_feedback_output(expected, output)

        name = 'mv_latest_status_videos'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file])
        expected = [
            FeedbackManager.info_processing_file(filename=file),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=name, version='(v1)'),
            FeedbackManager.success_create(name=f"{name}__v1")
        ]
        self._assert_feedback_output(expected, output)

        name = 'mv_videos'
        file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", file])
        expected = [
            FeedbackManager.info_processing_file(filename=file),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=name, version='(v1)'),
            FeedbackManager.success_create(name=f"{name}__v1")
        ]
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_push__materialized_override_not_create_two_VMs(self) -> None:
        await self._auth()

        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        datasource_file.write("""
VERSION 0

SCHEMA >
    `id` UInt32,
    `views` UInt64

ENGINE "MergeTree"
            """)
        datasource_file.seek(0)
        output = await self._tb(["push", datasource_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=datasource_name, version='(v0)'),
            FeedbackManager.success_create(name=f"{datasource_name}__v0")
        ]
        self._assert_feedback_output(expected, output)

        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe')
        pipe_file.write(f"""
VERSION 0

NODE mt
SQL >
    SELECT toUInt32(a) as id, toUInt32(a * 100) as views FROM test_table

TYPE MATERIALIZED
DATASOURCE {datasource_name}
            """)
        pipe_file.seek(0)
        output = await self._tb(["push", pipe_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=pipe_name, version='(v0)'),
            FeedbackManager.success_create(name=f"{pipe_name}__v0")
        ]
        self._assert_feedback_output(expected, output)

        pipe_file.write(f"""
VERSION 0

NODE mt
SQL >
    SELECT toUInt32(a) as id, toUInt32(a * 100) as views FROM test_table

TYPE MATERIALIZED
DATASOURCE {datasource_name}
            """)

        pipe_name__v0 = f"{pipe_name}__v0"
        pipe_file.seek(0)
        output = await self._tb(["push", pipe_file.name, "--force"])
        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_resource(name=pipe_name, version=0, latest_version=0),
            FeedbackManager.info_materialized_datasource_used(pipe=pipe_name__v0, datasource=f"{datasource_name}__v0"),
            FeedbackManager.success_create(name=pipe_name__v0)
        ]
        self._assert_feedback_output(expected, output)

        # We shouldn't be pushing the checker as MV, so we shouldn't get this message twice
        self._assert_feedback_output([
            f"{FeedbackManager.info_materialized_datasource_used(pipe=pipe_name__v0, datasource=f'{datasource_name}__v0')}{FeedbackManager.info_materialized_datasource_used(pipe=pipe_name__v0, datasource=f'{datasource_name}__v0')}"
        ], output, not_in=True)

    @tornado.testing.gen_test
    async def test_push__materialized_override_datasource(self) -> None:
        await self._auth()

        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        datasource_file.write("""
VERSION 0

SCHEMA >
    `id` UInt64,
    `views` UInt64

ENGINE "MergeTree"
            """)
        datasource_file.seek(0)
        output = await self._tb(["push", datasource_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=datasource_name, version='(v0)'),
            FeedbackManager.success_create(name=f"{datasource_name}__v0")
        ]
        self._assert_feedback_output(expected, output)

        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe')
        pipe_file.write(f"""
VERSION 0

NODE mt
SQL >
    SELECT sum(a) as id, toUInt64(a * 100) as views FROM test_table
    GROUP BY views

TYPE MATERIALIZED
DATASOURCE {datasource_name}
ENGINE SummingMergeTree\nENGINE_SORTING_KEY views
            """)
        pipe_file.seek(0)
        output = await self._tb(["push", pipe_file.name], assert_exit_code=1)
        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=pipe_name, version='(v0)'),
            'If you want to try to force override the Materialized View, please use the `--override-datasource` flag'
        ]
        self._assert_feedback_output(expected, output)

        output = await self._tb(["push", pipe_file.name, '--override-datasource'])
        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=pipe_name, version='(v0)'),
            FeedbackManager.success_create(name=f"{pipe_name}__v0")
        ]
        self._assert_feedback_output(expected, output)
        pipe_name__v0 = f"{pipe_name}__v0"
        output = await self._tb(['pipe', 'rm', pipe_name__v0, '--yes'])

        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe')
        pipe_file.write(f"""
VERSION 0

NODE mt
SQL >
    SELECT toUInt64(a) as id, toUInt64(a * 100) as views FROM test_table

TYPE MATERIALIZED
DATASOURCE {datasource_name}
ENGINE MergeTree\nENGINE_SORTING_KEY id
            """)

        pipe_name__v0 = f"{pipe_name}__v0"
        pipe_file.seek(0)
        output = await self._tb(["push", pipe_file.name, '--override-datasource'])
        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=pipe_name, version='(v0)'),
            FeedbackManager.success_create(name=pipe_name__v0)
        ]
        self._assert_feedback_output(expected, output)

        # We shouldn't be pushing the checker as MV, so we shouldn't get this message twice
        self._assert_feedback_output([
            f"{FeedbackManager.info_materialized_datasource_used(pipe=pipe_name__v0, datasource=f'{datasource_name}__v0')}{FeedbackManager.info_materialized_datasource_used(pipe=pipe_name__v0, datasource=f'{datasource_name}__v0')}"
        ], output, not_in=True)

        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe')
        pipe_file.write(f"""
VERSION 0

NODE mt
SQL >
    SELECT toUInt64(a) as id, toUInt64(a) as _id, toUInt64(a * 100) as views FROM test_table

TYPE MATERIALIZED
DATASOURCE {datasource_name}
ENGINE MergeTree\nENGINE_SORTING_KEY id, _id
            """)

        pipe_name__v0 = f"{pipe_name}__v0"
        pipe_file.seek(0)
        output = await self._tb(["push", pipe_file.name, '--override-datasource', '--force'])
        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=pipe_name, version='(v0)'),
            FeedbackManager.success_create(name=pipe_name__v0)
        ]
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_push__materialized_override_checker(self) -> None:
        await self._auth()

        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        datasource_file.write("""
VERSION 0

SCHEMA >
    `id` UInt32,
    `views` UInt64

ENGINE "MergeTree"
            """)
        datasource_file.seek(0)
        output = await self._tb(["push", datasource_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=datasource_name, version='(v0)'),
            FeedbackManager.success_create(name=f"{datasource_name}__v0")
        ]
        self._assert_feedback_output(expected, output)

        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe')
        pipe_file.write(f"""
VERSION 0

NODE mt
SQL >
    SELECT toUInt32(a) as id, toUInt32(a * 100) as views FROM test_table

TYPE MATERIALIZED
DATASOURCE {datasource_name}
            """)

        pipe_name__v0 = f"{pipe_name}__v0"
        pipe_file.seek(0)
        output = await self._tb(["push", pipe_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=pipe_name, version='(v0)'),
            FeedbackManager.success_create(name=pipe_name__v0)
        ]
        self._assert_feedback_output(expected, output)

        pipe_file.write(f"""
VERSION 0

NODE mt
SQL >
    SELECT toUInt64(a) as id, toUInt32(a * 100) as views FROM test_table

TYPE MATERIALIZED
DATASOURCE {datasource_name}
            """)
        pipe_file.seek(0)
        output = await self._tb(["push", pipe_file.name, "--force"],
                                assert_exit_code=1)
        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file.name),
            FeedbackManager.warning_file_not_found_inside(name='test_table', folder='.'),
            FeedbackManager.warning_file_not_found_inside(name=datasource_name, folder='.'),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_resource(name=pipe_name, version=0, latest_version=0),
            'Cannot materialize node:',
            'Incompatible column types',
            'If you want to try to force override the Materialized View, please use the `--override-datasource` flag'
        ]

        self._assert_feedback_output(expected, output)

        # We shouldn't be pushing the checker as MV, so we shouldn't get this message twice
        self._assert_feedback_output([
            f"{FeedbackManager.info_materialized_datasource_used(pipe=pipe_name__v0, datasource=f'{datasource_name}__v0')}{FeedbackManager.info_materialized_datasource_used(pipe=pipe_name__v0, datasource=f'{datasource_name}__v0')}"
        ], output, not_in=True)

    @tornado.testing.gen_test
    async def test_push__pipe_materialized_check_column_types_match(self) -> None:
        await self._auth()

        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        datasource_file.write("""
VERSION 0

SCHEMA >
    `id` UInt32,
    `views` UInt64

ENGINE "MergeTree"
            """)
        datasource_file.seek(0)
        output = await self._tb(["push", datasource_file.name])

        expected = [
            FeedbackManager.info_processing_file(filename=datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=datasource_name, version='(v0)'),
            FeedbackManager.success_create(name=f"{datasource_name}__v0")
        ]
        self._assert_feedback_output(expected, output)

        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe')
        pipe_file.write(f"""
VERSION 0

NODE mt
SQL >
    SELECT toUInt32(a) as id, toFloat32(a * 100) as views FROM test_table

TYPE MATERIALIZED
DATASOURCE {datasource_name}
            """)
        pipe_file.seek(0)
        output = await self._tb(["push", pipe_file.name],
                                assert_exit_code=1)

        expected = [
            "Incompatible column types:",
            "** Column 1:",
            "** Data Source:  ('views', 'UInt64')",
            "** Pipe:\t ('views', 'Float32')",
            "** Error:\t Automatic conversion from Float32 to UInt64 is not supported: Float32 might contain values that won't fit inside a column of type UInt64",
        ]
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_push__pipe_materialized_warnings(self) -> None:
        await self._auth()

        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        datasource_file.write("""
VERSION 0

SCHEMA >
    `c` AggregateFunction(count),
    `a` Int32

ENGINE "AggregatingMergeTree"
ENGINE_SORTING_KEY "a"
            """)
        datasource_file.seek(0)
        output = await self._tb(["push", datasource_file.name])

        expected = [
            FeedbackManager.info_processing_file(filename=datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=datasource_name, version='(v0)'),
            FeedbackManager.success_create(name=f"{datasource_name}__v0"),
        ]
        self._assert_feedback_output(expected, output)

        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe')
        pipe_file.write(f"""
VERSION 0

NODE mt
SQL >
    SELECT countState() as c
    FROM (
        SELECT a, a as a1 FROM test_table)
    GROUP BY a

TYPE MATERIALIZED
DATASOURCE {datasource_name}
            """)
        pipe_file.seek(0)
        output = await self._tb(["push", pipe_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=pipe_name, version='(v0)'),
            FeedbackManager.success_create(name=f"{pipe_name}__v0"),
            "Column 'a' is present in the GROUP BY but not in the SELECT clause. This might indicate a not valid Materialized View, please make sure you aggregate and GROUP BY in the topmost query."
        ]
        self._assert_feedback_output(expected, output)

        # it should happen even if the users force the push
        output = await self._tb(["push", pipe_file.name, "--force"])
        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_resource(name=pipe_name, version='0', latest_version='0'),
            FeedbackManager.success_create(name=f"{pipe_name}__v0"),
            "Column 'a' is present in the GROUP BY but not in the SELECT clause. This might indicate a not valid Materialized View, please make sure you aggregate and GROUP BY in the topmost query."
        ]
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_creating_materialize_view_with_materialized_column(self) -> None:
        await self._auth()

        (source_datasource_file, source_datasource_name) = self.create_tmp_file(suffix='.datasource')
        source_datasource_file.write("""
VERSION 0

SCHEMA >
    `row` UInt32,
    `name` String MATERIALIZED toString(row)

ENGINE "MergeTree"
            """)
        source_datasource_file.seek(0)
        output = await self._tb(["push", source_datasource_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=source_datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=source_datasource_name, version='(v0)'),
            FeedbackManager.success_create(name=f"{source_datasource_name}__v0")
        ]
        self._assert_feedback_output(expected, output)

        (dst_datasource_file, dst_datasource_name) = self.create_tmp_file(suffix='.datasource')
        dst_datasource_file.write("""
VERSION 0

SCHEMA >
    `name` String

ENGINE "MergeTree"
            """)
        dst_datasource_file.seek(0)
        output = await self._tb(["push", dst_datasource_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=dst_datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=dst_datasource_name, version='(v0)'),
            FeedbackManager.success_create(name=f"{dst_datasource_name}__v0")
        ]
        self._assert_feedback_output(expected, output)

        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe')
        pipe_file.write(f"""
VERSION 0

NODE mt
SQL >
    SELECT name
    FROM {source_datasource_name}

TYPE MATERIALIZED
DATASOURCE {dst_datasource_name}
    """)
        pipe_file.seek(0)
        output = await self._tb(["push", pipe_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=pipe_name, version='(v0)'),
            FeedbackManager.success_create(name=f"{pipe_name}__v0")
        ]
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_creating_materialize_view_with_staging(self) -> None:
        await self._auth()

        (source_datasource_file, source_datasource_name) = self.create_tmp_file(suffix='.datasource')
        source_datasource_file.write("""
VERSION 0

SCHEMA >
    `pk` UInt64,
    `sku_rank` String

ENGINE "Null"
            """)
        source_datasource_file.seek(0)
        output = await self._tb(["push", source_datasource_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=source_datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=source_datasource_name, version='(v0)'),
            FeedbackManager.success_create(name=f"{source_datasource_name}__v0")
        ]
        self._assert_feedback_output(expected, output)

        (dst_datasource_file, dst_datasource_name) = self.create_tmp_file(suffix='.datasource')
        dst_datasource_file.write("""
VERSION 0

SCHEMA >
    `pk` UInt64,
    `sku_rank` String,
    `insert_date` DateTime

ENGINE "ReplacingMergeTree"
ENGINE_VER "insert_date"
ENGINE_SORTING_KEY "pk"
            """)
        dst_datasource_file.seek(0)
        output = await self._tb(["push", dst_datasource_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=dst_datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=dst_datasource_name, version='(v0)'),
            FeedbackManager.success_create(name=f"{dst_datasource_name}__v0")
        ]
        self._assert_feedback_output(expected, output)

        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe')
        pipe_file.write(f"""
VERSION 0

NODE mt
SQL >
    SELECT *, now() as insert_date
    FROM {source_datasource_name}

TYPE MATERIALIZED
DATASOURCE {dst_datasource_name}

TAGS "with_staging=true"
    """)
        pipe_file.seek(0)
        output = await self._tb(["push", pipe_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=pipe_name, version='(v0)'),
            FeedbackManager.success_create(name=f"{pipe_name}__v0")
        ]
        self._assert_feedback_output(expected, output)

        params = {
            'token': self.admin_token
        }
        response = await self.fetch_async(f'/v0/pipes/{pipe_name}__v0?{urlencode(params)}')
        self.assertEqual(response.code, 200, response.body)
        result = json.loads(response.body)
        self.assertEqual(result['nodes'][0]['tags'], {"staging": True})

    @tornado.testing.gen_test
    async def test_endpoint_with_datetime64_parameter(self) -> None:
        await self._auth()

        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe')
        pipe_file.write("""
NODE endpoint
SQL >
    %
    SELECT now() > parseDateTime64BestEffort({{DateTime64(timestamp, '2020-09-09 10:10:10.000')}}) as x
""")
        pipe_file.seek(0)
        output = await self._tb(["push", pipe_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.success_create(name=pipe_name)
        ]

        self._assert_feedback_output(expected, output)

        params = {
            'token': self.admin_token
        }
        response = await self.fetch_async(f'/v0/pipes/{pipe_name}.json?{urlencode(params)}')
        self.assertEqual(response.code, 200, response.body)
        result = json.loads(response.body)
        self.assertEqual(result['data'][0]['x'], 1, result)

    @tornado.testing.gen_test
    async def test_skipping_included_files(self) -> None:
        await self._auth()

        (source_datasource_file, source_datasource_name) = self.create_tmp_file(suffix='.datasource.incl')
        source_datasource_file.write("""
VERSION 0

SCHEMA >
    `pk` UInt64,
    `sku_rank` String

ENGINE "Null"
            """)
        source_datasource_file.seek(0)
        output = await self._tb(["push", source_datasource_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=source_datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=source_datasource_name, version='(v0)'),
            FeedbackManager.warning_skipping_include_file(file=source_datasource_file.name)
        ]
        self._assert_feedback_output(expected, output)

        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe.incl')
        pipe_file.write("""
NODE endpoint
SQL >
    %
    SELECT now() > parseDateTime64BestEffort({{DateTime64(timestamp, '2020-09-09 10:10:10.000')}}) as x
""")
        pipe_file.seek(0)
        output = await self._tb(["push", pipe_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.warning_skipping_include_file(file=pipe_file.name)
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_skipping_when_pushing_older_versions(self) -> None:
        await self._auth()

        (source_datasource_file, source_datasource_name) = self.create_tmp_file(suffix='.datasource')
        source_datasource_file.write("""
VERSION 0

SCHEMA >
    `row` UInt32,
    `name` String MATERIALIZED toString(row)

ENGINE "MergeTree"
            """)
        source_datasource_file.seek(0)
        output = await self._tb(["push", source_datasource_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=source_datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=source_datasource_name, version='(v0)'),
            FeedbackManager.success_create(name=f"{source_datasource_name}__v0")
        ]
        self._assert_feedback_output(expected, output)

        source_datasource_file.write("""
VERSION 1

SCHEMA >
    `row` UInt32,
    `name` String MATERIALIZED toString(row)

ENGINE "MergeTree"
            """)
        source_datasource_file.seek(0)
        output = await self._tb(["push", source_datasource_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=source_datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_resource(name=source_datasource_name, version=1, latest_version=0),
            FeedbackManager.success_create(name=f"{source_datasource_name}__v1")
        ]
        self._assert_feedback_output(expected, output)

        source_datasource_file.write("""
VERSION 0

SCHEMA >
    `row` UInt32,
    `name` String MATERIALIZED toString(row)

ENGINE "MergeTree"
            """)
        source_datasource_file.seek(0)
        output = await self._tb(["push", source_datasource_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=source_datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.warning_name_already_exists(name=f"{source_datasource_name}__v0")
        ]
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test()
    async def test_retry_when_hitting_rate_limit_table_creation(self) -> None:
        await self._auth()

        with User.transaction(self.WORKSPACE_ID) as w:
            w.set_rate_limit_config('api_datasources_create_schema', 1, 5, 0)

        for _ in range(3):
            (source_datasource_file, source_datasource_name) = self.create_tmp_file(suffix='.datasource')
            source_datasource_file.write("""
VERSION 0

SCHEMA >
    `row` UInt32,
    `name` String

ENGINE "MergeTree"
                """)
            source_datasource_file.seek(0)
            output = await self._tb(["push", source_datasource_file.name])
            expected = [
                FeedbackManager.info_processing_file(filename=source_datasource_file.name),
                FeedbackManager.info_building_dependencies(),
                FeedbackManager.info_processing_new_resource(name=source_datasource_name, version='(v0)'),
                FeedbackManager.success_create(name=f"{source_datasource_name}__v0")
            ]
            self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test()
    async def test_retry_when_hitting_rate_limit_appends_csv(self) -> None:
        await self._auth()

        with User.transaction(self.WORKSPACE_ID) as w:
            w.set_rate_limit_config('api_datasources_create_append_replace', 1, 5, 0)

        (source_datasource_file, source_datasource_name) = self.create_tmp_file(suffix='.datasource')
        source_datasource_file.write("""
VERSION 0

SCHEMA >
    `row` UInt32,
    `name` String

ENGINE "MergeTree"
            """)
        source_datasource_file.seek(0)
        output = await self._tb(["push", source_datasource_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=source_datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=source_datasource_name, version='(v0)'),
            FeedbackManager.success_create(name=f"{source_datasource_name}__v0")
        ]
        self._assert_feedback_output(expected, output)

        for i in range(3):
            (data_file, data_file_name) = self.create_tmp_file(suffix='.csv')
            data_file.write(f"""
                {i}, Hello
                {i+1}, World\
            """)
            data_file.seek(0)

            output = await self._tb(["datasource", "append", f"{source_datasource_name}__v0", data_file.name])
            expected = [
                FeedbackManager.info_starting_import_process(),
                FeedbackManager.success_progress_blocks(),
                FeedbackManager.success_total_rows(datasource=f"{source_datasource_name}__v0", total_rows=2 + (2 * i)),
                FeedbackManager.success_appended_datasource(datasource=f"{source_datasource_name}__v0"),
                FeedbackManager.info_data_pushed(datasource=f"{source_datasource_name}__v0")
            ]
            self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test()
    async def test_retry_when_hitting_rate_limit_appends_ndjson(self) -> None:
        await self._auth()

        with User.transaction(self.WORKSPACE_ID) as w:
            w.set_rate_limit_config('api_datasources_create_append_replace', 1, 5, 0)

        (source_datasource_file, source_datasource_name) = self.create_tmp_file(suffix='.datasource')
        source_datasource_file.write("""
VERSION 0

SCHEMA >
    `row` UInt32 `json:$.row`,
    `name` String `json:$.name`

ENGINE "MergeTree"
            """)
        source_datasource_file.seek(0)
        output = await self._tb(["push", source_datasource_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=source_datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=source_datasource_name, version='(v0)'),
            FeedbackManager.success_create(name=f"{source_datasource_name}__v0")
        ]
        self._assert_feedback_output(expected, output)

        for i in range(3):
            (data_file, data_file_name) = self.create_tmp_file(suffix='.ndjson')
            data_file.write(json.dumps({'row': i, 'name': f'Number {i}'}))
            data_file.seek(0)

            output = await self._tb(["datasource", "append", f"{source_datasource_name}__v0", data_file.name])
            expected = [
                FeedbackManager.info_starting_import_process(),
                FeedbackManager.success_progress_blocks(),
                FeedbackManager.success_total_rows(datasource=f"{source_datasource_name}__v0", total_rows=1 + (1 * i)),
                FeedbackManager.success_appended_datasource(datasource=f"{source_datasource_name}__v0"),
                FeedbackManager.info_data_pushed(datasource=f"{source_datasource_name}__v0")
            ]
            self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test()
    async def test_push_ecommerce_complete_project(self) -> None:
        await self._auth()

        base_directory = os.path.dirname(__file__) + '/projects/ecommerce'
        output = await self._tb(['push', "--folder", base_directory, '--push-deps', '--fixtures'])
        expected = [
            FeedbackManager.info_processing_file(filename=f"{base_directory}/datasources/events.datasource"),
            FeedbackManager.info_processing_file(filename=f"{base_directory}/datasources/current_events.datasource"),
            FeedbackManager.info_processing_new_resource(name='events', version=''),
            FeedbackManager.info_processing_new_resource(name='current_events', version=''),
            FeedbackManager.success_create(name='events'),
            FeedbackManager.success_create(name='current_events'),
            FeedbackManager.info_processing_file(filename=f"{base_directory}/datasources/events.datasource", size='544.0 b'),

            # TODO: This should be a CSV as we didn't define a JSON Path or maybe a more generic message of no file found
            FeedbackManager.warning_file_not_found(name=f'{base_directory}/datasources/fixtures/current_events.ndjson'),
        ]
        self._assert_feedback_output(expected, output)

        output = await self._tb(["sql", "SELECT count() FROM events", "--format", "csv"])
        expected = ['9']
        self._assert_feedback_output(expected, output)

        output = await self._tb(["sql", "SELECT count() FROM current_events", "--format", "csv"])
        expected = ['9']
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_push__should_return_a_good_error_with_invalid_engine_settings(self) -> None:
        await self._auth()

        name = 'test_ds_invalid_settings'
        file = self._get_resource_path(f'{name}.datasource')

        output = await self._tb(["push", file], assert_exit_code=1)
        expected = [
            FeedbackManager.info_processing_file(filename=file),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=name, version=''),
        ]
        self._assert_feedback_output(expected, output)

        final_error = "Failed creating Data Source: Invalid data source structure: The value for 'merge_with_ttl_timeout' can only be reduced if 'ttl_only_drop_parts' is active. Contact support@tinybird.co if you require access to this feature"
        self.assertTrue(final_error in output)

    @tornado.testing.gen_test
    async def test_push_and_sharing_datasource(self):
        await self._auth()

        # We create one workspace to share to
        (workspace_to_create, _) = await self._create_extra_workspace()

        # Another workspace to share to
        (workspace_to_create_2, _) = await self._create_extra_workspace()

        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        datasource_file.write(f"""
VERSION 0

SCHEMA >
    `row` UInt32,
    `name` String

SHARED_WITH >
    {workspace_to_create}
    {workspace_to_create_2}

ENGINE "MergeTree"
            """)
        datasource_file.seek(0)
        output = await self._tb(["push", datasource_file.name, "--user_token", self.user_token])
        expected = [
            FeedbackManager.info_processing_file(filename=datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=datasource_name, version='(v0)'),
            FeedbackManager.success_create(name=f"{datasource_name}__v0"),
            FeedbackManager.success_datasource_shared(datasource=f"{datasource_name}__v0", workspace=workspace_to_create),
            FeedbackManager.success_datasource_shared(datasource=f"{datasource_name}__v0", workspace=workspace_to_create_2)
        ]
        self._assert_feedback_output(expected, output)

        # Let's try to use the new datasource
        output = await self._tb(["workspace", "use", workspace_to_create])
        self._assert_feedback_output([f"Now using {workspace_to_create}"], output)

        (endpoint_file, endpoint_name) = self.create_tmp_file(suffix='.pipe')
        endpoint_file.write(f"""
NODE endpoint
SQL >
    SELECT *
    FROM {self.WORKSPACE}.{datasource_name}
            """)

        endpoint_file.seek(0)
        output = await self._tb(["push", endpoint_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=endpoint_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=endpoint_name, version=''),
            FeedbackManager.success_create(name=endpoint_name)
        ]

        self._assert_feedback_output(expected, output)

        # Let's try to use the new datasource in the other workspace
        output = await self._tb(["workspace", "use", workspace_to_create_2])
        self._assert_feedback_output([f"Now using {workspace_to_create_2}"], output)

        (endpoint_file, endpoint_name) = self.create_tmp_file(suffix='.pipe')
        endpoint_file.write(f"""
NODE endpoint
SQL >
    SELECT *
    FROM {self.WORKSPACE}.{datasource_name}
            """)

        endpoint_file.seek(0)
        output = await self._tb(["push", endpoint_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=endpoint_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=endpoint_name, version=''),
            FeedbackManager.success_create(name=endpoint_name)
        ]

        self._assert_feedback_output(expected, output)

        # Let's try to unshare the datasource
        output = await self._tb(["workspace", "use", self.WORKSPACE])
        self._assert_feedback_output([f"Now using {self.WORKSPACE}"], output)

        datasource_file.truncate()
        datasource_file.write(f"""
VERSION 0

SCHEMA >
    `row` UInt32,
    `name` String

SHARED_WITH >
    {workspace_to_create}

ENGINE "MergeTree"
            """)
        datasource_file.seek(0)
        output = await self._tb(["push", datasource_file.name, "--user_token", self.user_token, "--force"])
        expected = [
            FeedbackManager.info_processing_file(filename=datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.success_datasource_unshared(datasource=f"{datasource_name}__v0", workspace=workspace_to_create_2),
            FeedbackManager.warning_datasource_already_exists(datasource=f"{datasource_name}__v0")
        ]
        self._assert_feedback_output(expected, output)

        (endpoint_file, endpoint_name) = self.create_tmp_file(suffix='.pipe')
        endpoint_file.write(f"""
NODE endpoint
SQL >
    SELECT *
    FROM {self.WORKSPACE}.{datasource_name}
            """)

        endpoint_file.seek(0)
        output = await self._tb(["push", endpoint_file.name], assert_exit_code=1)
        expected = [
            FeedbackManager.info_processing_file(filename=endpoint_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=endpoint_name, version=''),
            FeedbackManager.error_push_file_exception(filename=endpoint_file, error=''),
            FeedbackManager.error_pushing_pipe(pipe=endpoint_name, error=f"Resource '{self.WORKSPACE}_{datasource_name}' not found")
        ]

    @tornado.testing.gen_test
    async def test_sharing_datasource_without_passing_user_token(self):
        await self._auth()

        # We create one workspace to share to
        (workspace_to_create, _) = await self._create_extra_workspace()

        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        datasource_file.write(f"""
VERSION 0

SCHEMA >
    `row` UInt32,
    `name` String

SHARED_WITH >
    {workspace_to_create}

ENGINE "MergeTree"
            """)
        datasource_file.seek(0)
        output = await self._tb(["push", datasource_file.name], input=self.user_token)
        expected = [
            FeedbackManager.info_processing_file(filename=datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=datasource_name, version='(v0)'),
            FeedbackManager.success_create(name=f"{datasource_name}__v0")
        ]
        self._assert_feedback_output(expected, output)

        # Let's try to use the new datasource
        output = await self._tb(["workspace", "use", workspace_to_create])
        self._assert_feedback_output([f"Now using {workspace_to_create}"], output)

        (endpoint_file, endpoint_name) = self.create_tmp_file(suffix='.pipe')
        endpoint_file.write(f"""
NODE endpoint
SQL >
    SELECT *
    FROM {self.WORKSPACE}.{datasource_name}
            """)

        endpoint_file.seek(0)
        output = await self._tb(["push", endpoint_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=endpoint_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=endpoint_name, version=''),
            FeedbackManager.success_create(name=endpoint_name)
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_trying_to_share_datasource_to_not_existing_workspace(self):
        await self._auth()

        # We create one workspace to share to
        (workspace_to_create, _) = await self._create_extra_workspace()

        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        datasource_file.write(f"""
VERSION 0

SCHEMA >
    `row` UInt32,
    `name` String

SHARED_WITH >
    {workspace_to_create}
    whatever

ENGINE "MergeTree"
            """)
        datasource_file.seek(0)
        output = await self._tb(["push", datasource_file.name], input=self.user_token,
                                assert_exit_code=1)
        expected = [
            FeedbackManager.info_processing_file(filename=datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=datasource_name, version='(v0)'),
            "Unable to share datasource with the workspace whatever. Review that you have the admin permissions on this workspace"
        ]
        self._assert_feedback_output(expected, output)

        # Let's try to use the new datasource
        output = await self._tb(["workspace", "use", workspace_to_create])
        self._assert_feedback_output([f"Now using {workspace_to_create}"], output)

        (endpoint_file, endpoint_name) = self.create_tmp_file(suffix='.pipe')
        endpoint_file.write(f"""
NODE endpoint
SQL >
    SELECT *
    FROM {self.WORKSPACE}.{datasource_name}
            """)

        endpoint_file.seek(0)
        output = await self._tb(["push", endpoint_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=endpoint_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=endpoint_name, version=''),
            FeedbackManager.success_create(name=endpoint_name),
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_share_datasource_using_workspace_mapping(self):
        await self._auth()

        # We create one workspace to share to
        (workspace_to_create, _) = await self._create_extra_workspace()

        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        datasource_file.write("""
VERSION 0

SCHEMA >
    `row` UInt32,
    `name` String

SHARED_WITH >
    whatever

ENGINE "MergeTree"
            """)
        datasource_file.seek(0)
        output = await self._tb(["push", datasource_file.name, "--workspace_map", "whatever", workspace_to_create], input=self.user_token)
        expected = [
            FeedbackManager.info_processing_file(filename=datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=datasource_name, version='(v0)'),
            FeedbackManager.success_create(name=f"{datasource_name}__v0")
        ]
        self._assert_feedback_output(expected, output)

        # Let's try to use the new datasource
        output = await self._tb(["workspace", "use", workspace_to_create])
        self._assert_feedback_output([f"Now using {workspace_to_create}"], output)

        (endpoint_file, endpoint_name) = self.create_tmp_file(suffix='.pipe')
        endpoint_file.write(f"""
NODE endpoint
SQL >
    SELECT *
    FROM {self.WORKSPACE}.{datasource_name}
            """)

        endpoint_file.seek(0)
        output = await self._tb(["push", endpoint_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=endpoint_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=endpoint_name, version=''),
            FeedbackManager.success_create(name=endpoint_name)
        ]

        self._assert_feedback_output(expected, output)


class TestCLIMaterialize(TestCLI):
    @tornado.testing.gen_test
    async def test_materialize_full_happy_path_no_versions(self) -> None:
        await self._auth()

        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        datasource_file.write("""
SCHEMA >
`id` UInt32,
`views` UInt64

ENGINE "MergeTree"
        """)
        datasource_file.seek(0)
        output = await self._tb(["push", datasource_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.success_create(name=datasource_name)
        ]
        self._assert_feedback_output(expected, output)

        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe')
        pipe_file.write(f"""
NODE mt
SQL >
SELECT id, views FROM {datasource_name}""")
        pipe_file.seek(0)
        # materialize using all options available
        output = await self._tb(['materialize', pipe_file.name, '--force-populate', 'subset', '--override-pipe', '--override-datasource'])

        expected = [
            FeedbackManager.warning_beta_tester(),
            FeedbackManager.info_before_push_materialize(name=pipe_file.name),
            FeedbackManager.info_before_materialize(name=pipe_name),
            FeedbackManager.info_pipe_backup_created(name=f'{pipe_file.name}_bak'),
            'Populating',
            FeedbackManager.success_created_matview(name=f'mv_{pipe_name}_mt')
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_materialize_full_happy_path_with_versions(self) -> None:
        await self._auth()

        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        datasource_file.write("""
VERSION 0

SCHEMA >
    `id` UInt32,
    `views` UInt64

ENGINE "MergeTree"
            """)
        datasource_file.seek(0)
        output = await self._tb(["push", datasource_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=datasource_name, version='(v0)'),
            FeedbackManager.success_create(name=f"{datasource_name}__v0")
        ]
        self._assert_feedback_output(expected, output)

        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe')
        pipe_file.write(f"""
VERSION 0

NODE mt
SQL >
    SELECT id, views FROM {datasource_name}""")
        pipe_file.seek(0)
        output = await self._tb(["materialize", pipe_file.name, '--force-populate', 'subset', '--override-pipe', '--override-datasource'])
        expected = [
            FeedbackManager.warning_beta_tester(),
            FeedbackManager.info_before_push_materialize(name=pipe_file.name),
            FeedbackManager.info_processing_new_resource(name=pipe_name, version='(v0)'),
            FeedbackManager.info_before_materialize(name=pipe_name),
            FeedbackManager.info_pipe_backup_created(name=f'{pipe_file.name}_bak'),
            FeedbackManager.success_generated_local_file(file=f'mv_{pipe_name}_mt.datasource'),
            FeedbackManager.success_generated_local_file(file=f'{pipe_name}.pipe'),
            FeedbackManager.success_created_matview(name=f'mv_{pipe_name}_mt'),
            'Populating'
        ]
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_materialize_full_happy_path_with_prefix_and_versions(self) -> None:
        await self._auth()

        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        datasource_file.write("""
VERSION 0

SCHEMA >
    `id` UInt32,
    `views` UInt64

ENGINE "MergeTree"
            """)
        datasource_file.seek(0)
        output = await self._tb(["push", datasource_file.name, '--prefix', 'tt'])
        expected = [
            FeedbackManager.info_processing_file(filename=datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=f'tt__{datasource_name}', version='(v0)'),
            FeedbackManager.success_create(name=f"tt__{datasource_name}__v0")
        ]
        self._assert_feedback_output(expected, output)

        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe')
        pipe_file.write(f"""
VERSION 0

NODE mt
SQL >
    SELECT id, views FROM {datasource_name}""")
        pipe_file.seek(0)
        output = await self._tb(["materialize", pipe_file.name, '--prefix', 'tt', '--force-populate', 'subset', '--override-pipe', '--override-datasource'])
        expected = [
            FeedbackManager.warning_beta_tester(),
            FeedbackManager.info_before_push_materialize(name=pipe_file.name),
            FeedbackManager.info_processing_new_resource(name=f'tt__{pipe_name}', version='(v0)'),
            FeedbackManager.info_before_materialize(name=f'tt__{pipe_name}__v0'),
            FeedbackManager.info_pipe_backup_created(name=f'{pipe_file.name}_bak'),
            FeedbackManager.success_generated_local_file(file=f'{pipe_name}_mt.datasource'),
            FeedbackManager.success_generated_local_file(file=f'{pipe_name}.pipe'),
            FeedbackManager.success_created_matview(name=f'tt__{pipe_name}_mt'),
            'Populating'
        ]
        self._assert_feedback_output(expected, output)


class TestCLIPull(TestCLI):
    @tornado.testing.gen_test
    async def test_pull__should_pull_all_data(self) -> None:
        await self._auth()

        datasource = f'{self.CLI_PROJECT_PATH}test_table.datasource'
        pipe = f'{self.CLI_PROJECT_PATH}test_pipe.pipe'

        output = await self._tb(["pull", f'--folder={self.CLI_PROJECT_PATH}'])
        expected = [
            FeedbackManager.info_writing_resource(resource=datasource, prefix=''),
            FeedbackManager.info_writing_resource(resource=pipe, prefix='')
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_pull__should_not_overwrite_interval(self) -> None:
        await self._auth()

        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe')

        datasource_file.write("""
SCHEMA >
`a1` Int64,
`a2` String,
`a3` DateTime

ENGINE "MergeTree"
        """)
        datasource_file.seek(0)
        await self._tb(["push", datasource_file.name])

        pipe_file.write(f"""
NODE mv
SQL >

    SELECT
        a1,
        a2,
        a3
    FROM {datasource_name}
    WHERE a3 > now() - interval 1 day
            """)

        pipe_file.seek(0)
        await self._tb(["push", pipe_file.name])

        downloaded_file = f'{self.CLI_PROJECT_PATH}{pipe_name}.pipe'
        output = await self._tb(["pull", f"--match={pipe_name}", f'--folder={self.CLI_PROJECT_PATH}'])

        expected = [
            FeedbackManager.info_writing_resource(resource=downloaded_file, prefix='')
        ]

        self._assert_feedback_output(expected, output)

        downloaded_file_content = Path(downloaded_file).read_text()
        self.assertTrue('WHERE a3 > now() - interval 1 day' in downloaded_file_content)

    @tornado.testing.gen_test
    async def test_pull__should_pull_data_source_correctly(self) -> None:
        await self._auth()

        name = 'test_table'
        file = f'{self.CLI_PROJECT_PATH}{name}.datasource'
        output = await self._tb(["pull", f"--match={name}", f'--folder={self.CLI_PROJECT_PATH}'])
        expected = [
            FeedbackManager.info_writing_resource(resource=file, prefix='')
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_pull__should_skip_if_data_source_already_exists(self) -> None:
        await self._auth()

        name = 'test_table'
        file = f'{self.CLI_PROJECT_PATH}{name}.datasource'
        output = await self._tb(["pull", f"--match={name}", f'--folder={self.CLI_PROJECT_PATH}'])
        output = await self._tb(["pull", f"--match={name}", f'--folder={self.CLI_PROJECT_PATH}'])

        expected = [
            FeedbackManager.info_writing_resource(resource=file, prefix=''),
            FeedbackManager.info_skip_already_exists()
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_pull__should_show_prefixes_when_pulling_if_present(self) -> None:
        await self._auth()

        datasource = 'test_ds_a_good'
        file = self._get_resource_path(f'{datasource}.datasource')
        await self._tb(["push", file, "--prefix=dev", "--force"])

        pipe = 'test_pipe_a_good'
        file = self._get_resource_path(f'{pipe}.pipe')
        await self._tb(["push", file, "--prefix=dev", "--force"])

        output = await self._tb(["pull", f'--folder={self.CLI_PROJECT_PATH}'])

        ds_file = f'{self.CLI_PROJECT_PATH}{datasource}.datasource'
        pipe_file = f'{self.CLI_PROJECT_PATH}{pipe}.pipe'

        expected = [
            FeedbackManager.info_writing_resource(resource=ds_file, prefix='(dev)'),
            FeedbackManager.info_writing_resource(resource=pipe_file, prefix='(dev)'),
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_pull_should_download_the_datasource_with_practically_the_same_schema(self) -> None:
        await self._auth()

        name = 'test_datasource_with_different_columns'
        original_file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", original_file])

        expected = [
            FeedbackManager.info_processing_file(filename=original_file),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=name, version=''),
            FeedbackManager.success_create(name=name),
            FeedbackManager.info_not_pushing_fixtures()
        ]

        self._assert_feedback_output(expected, output)

        downloaded_file = f'{self.CLI_PROJECT_PATH}{name}.datasource'
        output = await self._tb(["pull", f"--match={name}", f'--folder={self.CLI_PROJECT_PATH}'])
        expected = [
            FeedbackManager.info_writing_resource(resource=downloaded_file, prefix='')
        ]

        self._assert_feedback_output(expected, output)

        original_file_content = Path(original_file).read_text()
        downloaded_file_content = Path(downloaded_file).read_text()

        self.assertEqual(original_file_content, downloaded_file_content)

    @tornado.testing.gen_test
    async def test_pull_should_download_the_datasource_with_practically_the_same_schema_but_versions(self) -> None:
        await self._auth()

        name = 'test_ds_a_good_with_version'
        original_file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", original_file])

        expected = [
            FeedbackManager.info_processing_file(filename=original_file),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=name, version='(v1)'),
            FeedbackManager.success_create(name=f'{name}__v1'),
            FeedbackManager.info_not_pushing_fixtures()
        ]

        self._assert_feedback_output(expected, output)

        name = 'test_pipe_a_good_with_version'
        original_file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", original_file])

        downloaded_file = f'{self.CLI_PROJECT_PATH}{name}.pipe'
        output = await self._tb(["pull", '--match=a_good_with_version', f'--folder={self.CLI_PROJECT_PATH}'])

        original_file_content = Path(original_file).read_text()
        downloaded_file_content = Path(downloaded_file).read_text()

        self.assertEqual(original_file_content, downloaded_file_content)

    @tornado.testing.gen_test
    async def test_pull__kafka_datasource(self) -> None:
        await self._auth()
        with patch.object(KafkaUtils, 'get_kafka_topic_group', return_value={'response': 'ok'}):
            name = 'kafka_datasource'
            original_file = self._get_resource_path(f'{name}.datasource')
            output = await self._tb(["push", original_file])

            self._assert_feedback_output([
                FeedbackManager.success_create(name=name)
            ], output)

            downloaded_file = f'{self.CLI_PROJECT_PATH}{name}.datasource'
            output = await self._tb(["pull", f"--match={name}", f'--folder={self.CLI_PROJECT_PATH}'])

            expected = [
                FeedbackManager.info_writing_resource(resource=downloaded_file, prefix='')
            ]

        self._assert_feedback_output(expected, output)

        downloaded_file_content = Path(downloaded_file).read_text()

        self.assertFalse('KAFKA_KEY ' in downloaded_file_content)
        self.assertFalse('KAFKA_PASSWORD' in downloaded_file_content)
        self.assertFalse('KAFKA_BOOTSTRAP_SERVERS' in downloaded_file_content)
        self.assertTrue("KAFKA_CONNECTION_NAME 'connection_name'" in downloaded_file_content)
        self.assertTrue('KAFKA_AUTO_OFFSET_RESET' in downloaded_file_content)
        self.assertTrue('KAFKA_TARGET_PARTITIONS' in downloaded_file_content)
        self.assertTrue('ENGINE_TTL' in downloaded_file_content)
        assert "`customColumn` Int64 `json:$.customColumn`" in downloaded_file_content

    @tornado.testing.gen_test
    async def test_pull__a_pulled_kafka_ds_can_be_pushed_again(self) -> None:
        await self._auth()
        with patch.object(KafkaUtils, 'get_kafka_topic_group', return_value={'response': 'ok'}):
            name = 'kafka_datasource'
            original_file = self._get_resource_path(f'{name}.datasource')
            output = await self._tb(["push", original_file])

            self._assert_feedback_output([
                FeedbackManager.success_create(name=name)
            ], output)

            downloaded_file = f'{self.CLI_PROJECT_PATH}{name}.datasource'
            output = await self._tb(["pull", f"--match={name}", f'--folder={self.CLI_PROJECT_PATH}'])

            self._assert_feedback_output([
                FeedbackManager.info_writing_resource(resource=downloaded_file, prefix='')
            ], output)

            output = await self._tb(["push", downloaded_file, '--force'])

            self._assert_feedback_output([
                FeedbackManager.warning_datasource_already_exists(datasource=name)
            ], output)

    @tornado.testing.gen_test
    async def test_pull__join_datasource(self) -> None:
        await self._auth()

        name = 'join_datasource'
        original_file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", original_file])

        self._assert_feedback_output([
            FeedbackManager.success_create(name=name)
        ], output)

        downloaded_file = f'{self.CLI_PROJECT_PATH}{name}.datasource'
        output = await self._tb(["pull", f"--match={name}", f'--folder={self.CLI_PROJECT_PATH}'])

        expected = [
            FeedbackManager.info_writing_resource(resource=downloaded_file, prefix='')
        ]

        self._assert_feedback_output(expected, output)

        downloaded_file_content = Path(downloaded_file).read_text()

        self.assertTrue('ENGINE "Join"' in downloaded_file_content)
        self.assertTrue('ENGINE_JOIN_STRICTNESS "ANY"' in downloaded_file_content)
        self.assertTrue('ENGINE_JOIN_TYPE "LEFT"' in downloaded_file_content)
        self.assertTrue('ENGINE_KEY_COLUMNS "key"' in downloaded_file_content)

        output = await self._tb(["push", downloaded_file, '--prefix=resubmit'])

        self._assert_feedback_output([
            FeedbackManager.success_create(name=f'resubmit__{name}')
        ], output)

    @tornado.testing.gen_test
    async def test_pull__ndjson_datasource(self) -> None:
        await self._auth()

        name = 'test_ds_a_good_jsonpath'
        original_file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", original_file])

        downloaded_file = f'{self.CLI_PROJECT_PATH}{name}.datasource'
        output = await self._tb(["pull", f"--match={name}", f'--folder={self.CLI_PROJECT_PATH}'])

        expected = [
            FeedbackManager.info_writing_resource(resource=downloaded_file, prefix='')
        ]

        self._assert_feedback_output(expected, output)

        downloaded_file_content = Path(downloaded_file).read_text()

        self.assertTrue('`json:$.a1`' in downloaded_file_content)
        self.assertTrue('`json:$.a2`' in downloaded_file_content)
        self.assertTrue('`json:$.a3`' in downloaded_file_content)

    @tornado.testing.gen_test
    async def test_pull__copy_pipe(self) -> None:
        with User.transaction(self.WORKSPACE_ID) as w:
            w.feature_flags[FeatureFlagWorkspaces.EXPORT.value] = True

        await self._auth()

        origin_ds_name = 'test_ds_a_good'
        origin_ds_file = self._get_resource_path(f'{origin_ds_name}.datasource')
        await self._tb(["push", origin_ds_file])

        target_ds_name = 'test_ds_a_good_with_description'
        target_ds_file = self._get_resource_path(f'{target_ds_name}.datasource')
        await self._tb(["push", target_ds_file])

        pipe_name = 'test_pipe_copy'
        pipe_filename = f'{pipe_name}.pipe'
        pipe_file = self._get_resource_path(pipe_filename)
        await self._tb(["push", pipe_file])

        downloaded_file = f'{self.CLI_PROJECT_PATH}{pipe_filename}'
        output = await self._tb(["pull", f"--match={pipe_name}", f'--folder={self.CLI_PROJECT_PATH}'])
        downloaded_file_content = Path(downloaded_file).read_text()

        expected = [
            FeedbackManager.info_writing_resource(resource=downloaded_file, prefix='')
        ]

        self._assert_feedback_output(expected, output)

        downloaded_file_content = Path(downloaded_file).read_text()

        self.assertTrue('TYPE copy' in downloaded_file_content)
        self.assertTrue(f'TARGET_DATASOURCE {target_ds_name}' in downloaded_file_content)
        self.assertTrue(f'TARGET_DATASOURCE {target_ds_name}' in downloaded_file_content)

        with User.transaction(self.WORKSPACE_ID) as w:
            w.feature_flags[FeatureFlagWorkspaces.EXPORT.value] = False


class TestCLISQL(TestCLI):
    @tornado.testing.gen_test
    async def test_sql__should_return_an_error_if_query_is_invalid(self) -> None:
        await self._auth()

        output = await self._tb(["sql", "SELECT * FROMM"])

        expected = [
            'Syntax error'
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_sql__should_return_an_error_on_insert(self) -> None:
        await self._auth()

        output = await self._tb(["sql", "INSERT INTO test_table VALUES 1, a, 3"])

        expected = [
            FeedbackManager.error_invalid_query(),
            FeedbackManager.info_append_data()
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_sql__should_return_an_error_if_is_forbidden(self) -> None:
        await self._auth()

        output = await self._tb(["sql", "SELECT * FROM wrong_ds"])

        expected = [
            FeedbackManager.error_exception(error="Forbidden: Resource 'wrong_ds' not found")
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_sql__should_run_query_successfuly(self) -> None:
        await self._auth()

        output = await self._tb(["sql", "SELECT * FROM test_table ORDER BY a"])

        expected = [
            'abc0123.56test11one22two33three44four10020.45test'
        ]

        self._assert_feedback_output(expected, self._clean_table(output))

    @tornado.testing.gen_test
    async def test_sql__should_return_json_format(self) -> None:
        await self._auth()

        output = await self._tb(["sql", "SELECT * FROM test_table", "--format=json"])

        expected = [
            json.dumps([{'name': 'a', 'type': 'UInt64'}, {'name': 'b', 'type': 'Float32'}, {'name': 'c', 'type': 'String'}]).replace(' ', '')
        ]

        self._assert_feedback_output(expected, self._clean_table(output))

    @tornado.testing.gen_test
    async def test_sql__should_return_csv_format(self) -> None:
        await self._auth()

        output = await self._tb(["sql", "SELECT * FROM test_table ORDER BY a", "--format=csv"])

        expected = [
            '"a","b","c"0,123.56,"test"1,1,"one"2,2,"two"3,3,"three"4,4,"four"100,-20.45,"test"'
        ]

        self._assert_feedback_output(expected, self._clean_output(output))

    @tornado.testing.gen_test
    async def test_sql__should_return_query_stats(self) -> None:
        await self._auth()

        output = await self._tb(["sql", "SELECT * FROM test_table", "--stats"])

        expected = [
            '** Query took',
            '** Rows read: 6',
            '** Bytes read: 149 bytes'
        ]

        self._assert_feedback_output(expected, self._clean_output(output))

    @tornado.testing.gen_test
    async def test_sql__with_pipeline(self) -> None:
        await self._auth()

        name = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.datasource')
        await self._tb(["push", file, '--force'])

        name = 'test_pipe_multiple_nodes'
        file = self._get_resource_path(f'{name}.pipe')
        await self._tb(["push", file, '--force'])

        output = await self._tb(["sql", "SELECT * FROM second_node", "--pipeline", "test_pipe_multiple_nodes"])
        self.assertTrue('** No rows' in output)

    @tornado.testing.gen_test
    async def test_sql__with_pipe_and_node(self) -> None:
        await self._auth()

        name = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.datasource')
        await self._tb(["push", file, '--force'])

        name = 'test_pipe_multiple_nodes'
        file = self._get_resource_path(f'{name}.pipe')
        await self._tb(["push", file, '--force'])

        output = await self._tb(["sql", "--pipe", file, "--node", "second_node"])
        self.assertTrue('** No rows' in output)

    @tornado.testing.gen_test
    async def test_running_huge_sql(self) -> None:
        await self._auth()

        sql = """
        SELECT *
        FROM (
            SELECT 0 as x UNION ALL
            SELECT 1 as x UNION ALL
            SELECT 2 as x UNION ALL
            SELECT 3 as x UNION ALL
            SELECT 4 as x UNION ALL
            SELECT 5 as x UNION ALL
            SELECT 6 as x UNION ALL
            SELECT 7 as x UNION ALL
            SELECT 8 as x UNION ALL
            SELECT 9 as x UNION ALL
            SELECT 10 as x UNION ALL
            SELECT 11 as x UNION ALL
            SELECT 12 as x UNION ALL
            SELECT 13 as x UNION ALL
            SELECT 14 as x UNION ALL
            SELECT 15 as x UNION ALL
            SELECT 16 as x UNION ALL
            SELECT 17 as x UNION ALL
            SELECT 18 as x UNION ALL
            SELECT 19 as x UNION ALL
            SELECT 20 as x UNION ALL
            SELECT 21 as x UNION ALL
            SELECT 22 as x UNION ALL
            SELECT 23 as x UNION ALL
            SELECT 24 as x UNION ALL
            SELECT 25 as x UNION ALL
            SELECT 26 as x UNION ALL
            SELECT 27 as x UNION ALL
            SELECT 28 as x UNION ALL
            SELECT 29 as x UNION ALL
            SELECT 30 as x UNION ALL
            SELECT 31 as x UNION ALL
            SELECT 32 as x UNION ALL
            SELECT 33 as x UNION ALL
            SELECT 34 as x UNION ALL
            SELECT 35 as x UNION ALL
            SELECT 36 as x UNION ALL
            SELECT 37 as x UNION ALL
            SELECT 38 as x UNION ALL
            SELECT 39 as x UNION ALL
            SELECT 40 as x UNION ALL
            SELECT 41 as x UNION ALL
            SELECT 42 as x UNION ALL
            SELECT 43 as x UNION ALL
            SELECT 44 as x UNION ALL
            SELECT 45 as x UNION ALL
            SELECT 46 as x UNION ALL
            SELECT 47 as x UNION ALL
            SELECT 48 as x UNION ALL
            SELECT 49 as x UNION ALL
            SELECT 50 as x UNION ALL
            SELECT 51 as x UNION ALL
            SELECT 52 as x UNION ALL
            SELECT 53 as x UNION ALL
            SELECT 54 as x UNION ALL
            SELECT 55 as x UNION ALL
            SELECT 56 as x UNION ALL
            SELECT 57 as x UNION ALL
            SELECT 58 as x UNION ALL
            SELECT 59 as x UNION ALL
            SELECT 60 as x UNION ALL
            SELECT 61 as x UNION ALL
            SELECT 62 as x UNION ALL
            SELECT 63 as x UNION ALL
            SELECT 64 as x UNION ALL
            SELECT 65 as x UNION ALL
            SELECT 66 as x UNION ALL
            SELECT 67 as x UNION ALL
            SELECT 68 as x UNION ALL
            SELECT 69 as x UNION ALL
            SELECT 70 as x UNION ALL
            SELECT 71 as x UNION ALL
            SELECT 72 as x UNION ALL
            SELECT 73 as x UNION ALL
            SELECT 74 as x UNION ALL
            SELECT 75 as x UNION ALL
            SELECT 76 as x UNION ALL
            SELECT 77 as x UNION ALL
            SELECT 78 as x UNION ALL
            SELECT 79 as x UNION ALL
            SELECT 80 as x UNION ALL
            SELECT 81 as x UNION ALL
            SELECT 82 as x UNION ALL
            SELECT 83 as x UNION ALL
            SELECT 84 as x UNION ALL
            SELECT 85 as x UNION ALL
            SELECT 86 as x UNION ALL
            SELECT 87 as x UNION ALL
            SELECT 88 as x UNION ALL
            SELECT 89 as x UNION ALL
            SELECT 90 as x UNION ALL
            SELECT 91 as x UNION ALL
            SELECT 92 as x UNION ALL
            SELECT 93 as x UNION ALL
            SELECT 94 as x UNION ALL
            SELECT 95 as x UNION ALL
            SELECT 96 as x UNION ALL
            SELECT 97 as x UNION ALL
            SELECT 98 as x UNION ALL
            SELECT 99 as x UNION ALL
            SELECT 100 as x UNION ALL
            SELECT 101 as x UNION ALL
            SELECT 102 as x UNION ALL
            SELECT 103 as x UNION ALL
            SELECT 104 as x UNION ALL
            SELECT 105 as x UNION ALL
            SELECT 106 as x UNION ALL
            SELECT 107 as x UNION ALL
            SELECT 108 as x UNION ALL
            SELECT 109 as x UNION ALL
            SELECT 110 as x UNION ALL
            SELECT 111 as x UNION ALL
            SELECT 112 as x UNION ALL
            SELECT 113 as x UNION ALL
            SELECT 114 as x UNION ALL
            SELECT 115 as x UNION ALL
            SELECT 116 as x UNION ALL
            SELECT 117 as x UNION ALL
            SELECT 118 as x UNION ALL
            SELECT 119 as x UNION ALL
            SELECT 120 as x UNION ALL
            SELECT 121 as x UNION ALL
            SELECT 122 as x UNION ALL
            SELECT 123 as x UNION ALL
            SELECT 124 as x UNION ALL
            SELECT 125 as x UNION ALL
            SELECT 126 as x UNION ALL
            SELECT 127 as x UNION ALL
            SELECT 128 as x UNION ALL
            SELECT 129 as x UNION ALL
            SELECT 130 as x UNION ALL
            SELECT 131 as x UNION ALL
            SELECT 132 as x UNION ALL
            SELECT 133 as x UNION ALL
            SELECT 134 as x UNION ALL
            SELECT 135 as x UNION ALL
            SELECT 136 as x UNION ALL
            SELECT 137 as x UNION ALL
            SELECT 138 as x UNION ALL
            SELECT 139 as x UNION ALL
            SELECT 140 as x UNION ALL
            SELECT 141 as x UNION ALL
            SELECT 142 as x UNION ALL
            SELECT 143 as x UNION ALL
            SELECT 144 as x UNION ALL
            SELECT 145 as x UNION ALL
            SELECT 146 as x UNION ALL
            SELECT 147 as x UNION ALL
            SELECT 148 as x UNION ALL
            SELECT 149 as x
        )
        ORDER BY x
        """

        self.assertTrue(len(sql) > MAX_GET_LENGTH)

        output = await self._tb(["sql", sql, "--format", "csv"])

        expected = [
            '0123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899'
        ]

        self._assert_feedback_output(expected, self._clean_output(output))


class TestCLIDatasourceAnalyze(TestCLI):
    @tornado.testing.gen_test
    async def test_analyze_url__should_print_csv_info_correctly(self) -> None:
        await self._auth()

        url = 'https://raw.githubusercontent.com/tinybirdco/ecommerce_data_project_advanced/main/datasources/fixtures/events.csv'
        output = await self._tb(["datasource", "analyze", url])

        expected = [
            'columnsnametypenullable',
            'column_00DateTimefalse',
            'column_01Stringfalse',
            'column_02Stringfalse',
            'column_03Stringfalse',
            'column_04Stringfalse',
            '**SQLSchema',
            '`column_00`DateTime,`column_01`String,`column_02`String,`column_03`String,`column_04`String',
            '**dialect',
            'namevalue',
            'delimiter,has_headerFalsenewline\\nescapecharNoneencodingutf8'
        ]

        self._assert_feedback_output(expected, self._clean_table(output))

    @tornado.testing.gen_test
    async def test_analyze_file__should_print_csv_info_correctly(self) -> None:
        await self._auth()

        file = self._get_fixture_path('small.csv')
        output = await self._tb(["datasource", "analyze", file])
        expected = [
            'uidInt16false'
            'qFloat32false'
            'vStringfalse'
            'dDateTimefalse'
            '**SQLSchema`uid`Int16,`q`Float32,`v`String,`d`DateTime',
            '**dialect',
            'namevalue',
            'delimiterhas_headerTruenewline\\nescapecharNoneencodingutf8'
        ]
        self._assert_feedback_output(expected, self._clean_table(output))

    @tornado.testing.gen_test
    async def test_analyze_url__should_print_ndjson_info_correctly(self) -> None:
        await self._auth()

        url = f'{HTTP_ADDRESS}/events.ndjson'
        output = await self._tb(["datasource", "analyze", url])

        expected = [
            'columnsnametypenullable',
            'dateDateTimefalse',
            'eventStringfalse',
            'extra_data_cityStringfalse',
            'product_idStringfalse',
            'user_idInt32false',
            'extra_data_priceNullable(Float32)true',
            'extra_data_termNullable(String)true',
            '**SQLSchema',
            'dateDateTime`json:$.date`,eventString`json:$.event`,extra_data_cityString`json:$.extra_data.city`,product_idString`json:$.product_id`,user_idInt32`json:$.user_id`,extra_data_priceNullable(Float32)`json:$.extra_data.price`,extra_data_termNullable(String)`json:$.extra_data.term`',
        ]

        self._assert_feedback_output(expected, self._clean_table(output))

    @tornado.testing.gen_test
    async def test_analyze_file__should_print_ndjson_info_correctly(self) -> None:
        await self._auth()

        file = self._get_resource_path('fixtures/events.ndjson')
        output = await self._tb(["datasource", "analyze", file])
        expected = [
            'columnsnametypenullable',
            'dateDateTimefalse',
            'eventStringfalse',
            'extra_data_cityStringfalse',
            'product_idStringfalse',
            'user_idInt32false',
            'extra_data_priceNullable(Float32)true',
            'extra_data_termNullable(String)true',
            '**SQLSchema',
            'dateDateTime`json:$.date`,eventString`json:$.event`,extra_data_cityString`json:$.extra_data.city`,product_idString`json:$.product_id`,user_idInt32`json:$.user_id`,extra_data_priceNullable(Float32)`json:$.extra_data.price`,extra_data_termNullable(String)`json:$.extra_data.term`',
        ]

        self._assert_feedback_output(expected, self._clean_table(output))

    @tornado.testing.gen_test
    async def test_analyze_url__should_print_parquet_info_correctly(self) -> None:
        await self._auth()

        url = f'{HTTP_ADDRESS}/hello_world.parquet'
        output = await self._tb(["datasource", "analyze", url])

        expected = [
            'columnsnametypenullable',
            'dateDateTimefalse',
            'idInt16false'
            'nameStringfalse'
            '**SQLSchema',
            'dateDateTime`json:$.date`,idInt16`json:$.id`,nameString`json:$.name`',
        ]

        self._assert_feedback_output(expected, self._clean_table(output))

    @tornado.testing.gen_test
    async def test_analyze_file__should_print_parquet_info_correctly(self) -> None:
        await self._auth()

        file = self._get_resource_path('fixtures/hello_world.parquet')
        output = await self._tb(["datasource", "analyze", file])

        expected = [
            'columnsnametypenullable',
            'dateDateTimefalse',
            'idInt16false'
            'nameStringfalse'
            '**SQLSchema',
            'dateDateTime`json:$.date`,idInt16`json:$.id`,nameString`json:$.name`',
        ]

        self._assert_feedback_output(expected, self._clean_table(output))


class TestCLIDatasourceAppendNDJSON(TestCLI):
    @tornado.testing.gen_test
    async def test_append__should_append_datasource_from_url_ndjson(self) -> None:
        await self._auth()

        file = self._get_resource_path('events.datasource')
        await self._tb(["push", file])

        url = f'{HTTP_ADDRESS}/events.ndjson'
        output = await self._tb(["datasource", "append", "events", f"{url}"])

        expected = [
            FeedbackManager.info_starting_import_process(),
            FeedbackManager.success_progress_blocks(),
            FeedbackManager.success_total_rows(datasource='events', total_rows=10),
            FeedbackManager.success_appended_datasource(datasource='events'),
            FeedbackManager.info_data_pushed(datasource='events')
        ]

        self._assert_feedback_output(expected, output)

        output = await self._tb(["sql", "SELECT product_id FROM events ORDER BY date DESC LIMIT 1", "--format", "JSON"])
        self.assertTrue(json.loads(output)['data'][0]['product_id'] == '670f5fb4-1aaa-11eb-b7cc-acde48001122')

    @tornado.testing.gen_test
    async def test_append__should_append_datasource_from_file_ndjson(self) -> None:
        await self._auth()

        file = self._get_resource_path('events_file.datasource')
        await self._tb(["push", file])

        file = self._get_resource_path('fixtures/events.ndjson')
        output = await self._tb(["datasource", "append", "events_file", file])
        expected = [
            FeedbackManager.info_starting_import_process(),
            FeedbackManager.success_progress_blocks(),
            FeedbackManager.success_total_rows(datasource='events_file', total_rows=10),
            FeedbackManager.success_appended_datasource(datasource='events_file'),
            FeedbackManager.info_data_pushed(datasource='events_file')
        ]

        self._assert_feedback_output(expected, output)

        output = await self._tb(["sql", "SELECT product_id FROM events_file ORDER BY date DESC LIMIT 1", "--format", "JSON"])
        self.assertTrue(json.loads(output)['data'][0]['product_id'] == '670f5fb4-1aaa-11eb-b7cc-acde48001122')

    @tornado.testing.gen_test
    async def test_append_uuid_values(self) -> None:
        await self._auth()

        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        datasource_file.write("""
SCHEMA >
    id UUID `json:$.id`

ENGINE "MergeTree"
ENGINE_PARTITION_KEY ""
ENGINE_SORTING_KEY tuple()
            """)

        datasource_file.seek(0)
        output = await self._tb(["push", datasource_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=datasource_name, version=''),
            FeedbackManager.success_create(name=datasource_name)
        ]

        self._assert_feedback_output(expected, output)

        (endpoint_file, endpoint_name) = self.create_tmp_file(suffix='.pipe')
        endpoint_file.write("""
NODE endpoint
SQL >
    SELECT id
    FROM generateRandom('id UUID')
    LIMIT 1000
            """)

        endpoint_file.seek(0)
        output = await self._tb(["push", endpoint_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=endpoint_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=endpoint_name, version=''),
            FeedbackManager.success_create(name=endpoint_name)
        ]

        self._assert_feedback_output(expected, output)

        output = await self._tb(["datasource", "append", datasource_name, f"{self.host}/v0/pipes/{endpoint_name}.ndjson?token={self.admin_token}"])
        expected = [
            FeedbackManager.info_starting_import_process(),
            FeedbackManager.success_progress_blocks(),
            FeedbackManager.success_total_rows(datasource=datasource_name, total_rows=1000),
            FeedbackManager.success_appended_datasource(datasource=datasource_name),
            FeedbackManager.info_data_pushed(datasource=datasource_name)
        ]
        self._assert_feedback_output(expected, output)


class TestCLIDatasourceAppend(TestCLI):
    @tornado.testing.gen_test
    async def test_append__should_require_arguments(self) -> None:
        await self._auth()

        url = 'https://raw.githubusercontent.com/tinybirdco/ecommerce_data_project_advanced/main/datasources/fixtures/events.csv'
        output = await self._tb(["datasource", "append", f"{url}"])

        expected = [
            FeedbackManager.error_missing_url_or_connector(datasource=url)
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_append__should_append_datasource_from_url(self) -> None:
        await self._auth()

        url = 'https://raw.githubusercontent.com/tinybirdco/ecommerce_data_project_advanced/main/datasources/fixtures/events.csv'
        output = await self._tb(["datasource", "append", "events", f"{url}"])

        expected = [
            FeedbackManager.info_starting_import_process(),
            FeedbackManager.success_progress_blocks(),
            FeedbackManager.success_total_rows(datasource='events', total_rows=9),
            FeedbackManager.success_appended_datasource(datasource='events'),
            FeedbackManager.info_data_pushed(datasource='events')
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_append__should_append_datasource_from_file(self) -> None:
        await self._auth()

        file = self._get_fixture_path('sales_0.csv')
        output = await self._tb(["datasource", "append", "sales_0", file])
        expected = [
            FeedbackManager.info_starting_import_process(),
            FeedbackManager.success_progress_blocks(),
            FeedbackManager.success_total_rows(datasource='sales_0', total_rows=2),
            FeedbackManager.success_appended_datasource(datasource='sales_0'),
            FeedbackManager.info_data_pushed(datasource='sales_0')
        ]

        self._assert_feedback_output(expected, output)


class TestCLIDatasourceTruncate(TestCLI):
    @tornado.testing.gen_test
    async def test_truncate__should_truncate_datasource(self) -> None:
        await self._auth()

        ds_name = "events_truncate"
        mv_node_name = "mypipe_0"
        mv_ds_name = "mv_cascade_events_truncate"

        with tempfile.NamedTemporaryFile(suffix=".csv", mode='w+', encoding='utf-8') as data_file:
            data_file_content = """2020-04-24 16:29:47,sku_0001,user_0000,login,"{}"
2020-04-24 16:29:47,sku_0001,user_0000,add_item_to_cart,"{}"
2020-04-24 16:29:47,sku_0001,user_0000,buy,"{}"
2020-04-24 16:29:47,sku_0001,user_0000,search,"{""term"": ""shirt""}"
2020-04-24 16:29:47,sku_0001,user_0000,saw,"{""price"": 34.3}"
2020-04-24 16:29:47,sku_0001,user_0000,buy,"{""price"": 34.3}"
2020-04-24 16:29:47,sku_0002,user_0001,buy,"{""price"": 34.3}"
2020-04-24 16:29:47,sku_0003,user_0000,buy,"{""price"": 34.3}"
2020-04-24 16:29:47,sku_0004,user_0002,buy,"{""price"": 34.3}"\
"""
            data_file.write(data_file_content)
            data_file.seek(0)

            output = await self._tb(["datasource", "append", ds_name, data_file.name])
            expected = [
                FeedbackManager.info_starting_import_process(),
                FeedbackManager.success_progress_blocks(),
                FeedbackManager.success_total_rows(datasource=ds_name, total_rows=9),
                FeedbackManager.success_appended_datasource(datasource=ds_name),
                FeedbackManager.info_data_pushed(datasource=ds_name)
            ]
            self._assert_feedback_output(expected, output)

            output = await self._tb(["sql", f"SELECT count() AS c FROM {ds_name}", "--format", "JSON"])
            self.assertTrue(json.loads(output)['data'][0]['c'] == 9, f"Failed count with {output}")

            with tempfile.NamedTemporaryFile(suffix=".pipe", mode='w+', encoding='utf-8') as pipe_file:
                pipe_file_content = f"""
                    NODE {mv_node_name}
                    SQL >
                        SELECT * FROM events_truncate

                    \nTYPE materialized\nDATASOURCE {mv_ds_name}\nENGINE MergeTree
                    """
                pipe_file.write(pipe_file_content)
                pipe_file.seek(0)
                pipe_name = os.path.basename(pipe_file.name).rsplit('.', 1)[0]

                output = await self._tb(["push", pipe_file.name])
                expected = [
                    FeedbackManager.info_processing_file(filename=pipe_file.name),
                    FeedbackManager.info_building_dependencies(),
                    FeedbackManager.info_processing_new_resource(name=pipe_name, version=""),
                    FeedbackManager.info_materialized_datasource_created(pipe=pipe_name, datasource=mv_ds_name),
                    FeedbackManager.success_create(name=pipe_name),
                    FeedbackManager.info_not_pushing_fixtures()
                ]

            self._assert_feedback_output(expected, output)

            output = await self._tb(["datasource", "append", mv_ds_name, data_file.name])
            expected = [
                FeedbackManager.info_starting_import_process(),
                FeedbackManager.success_progress_blocks(),
                FeedbackManager.success_total_rows(datasource=mv_ds_name, total_rows=9),
                FeedbackManager.success_appended_datasource(datasource=mv_ds_name),
                FeedbackManager.info_data_pushed(datasource=mv_ds_name)
            ]
            self._assert_feedback_output(expected, output)

            output = await self._tb(["sql", f"SELECT count() AS c FROM {mv_ds_name}", "--format", "JSON"])
            self.assertTrue(json.loads(output)['data'][0]['c'] == 9, f"Failed count with {output}")

            output = await self._tb(["datasource", "truncate", ds_name, "--yes", "--cascade"])

            expected = [
                FeedbackManager.success_truncate_datasource(datasource=ds_name),
                FeedbackManager.success_truncate_datasource(datasource=mv_ds_name)
            ]

            self._assert_feedback_output(expected, output)

            output = await self._tb(["sql", f"SELECT count() AS c FROM {ds_name}", "--format", "JSON"])
            self.assertTrue(json.loads(output)['data'][0]['c'] == 0, f"Failed count with {output}")

            output = await self._tb(["sql", f"SELECT count() AS c FROM {mv_ds_name}", "--format", "JSON"])
            self.assertTrue(json.loads(output)['data'][0]['c'] == 0, f"Failed count with {output}")


class TestCLIDatasourceReplace(TestCLI):
    @tornado.testing.gen_test
    async def test_replace__should_fully_replace_datasource_from_url(self) -> None:
        await self._auth()

        url = 'https://raw.githubusercontent.com/tinybirdco/ecommerce_data_project_advanced/main/datasources/fixtures/events.csv'
        output = await self._tb(["datasource", "append", "events_replaced", f"{url}"])

        expected = [
            FeedbackManager.info_starting_import_process(),
            FeedbackManager.success_progress_blocks(),
            FeedbackManager.success_total_rows(datasource='events_replaced', total_rows=9),
            FeedbackManager.success_appended_datasource(datasource='events_replaced'),
            FeedbackManager.info_data_pushed(datasource='events_replaced')
        ]

        self._assert_feedback_output(expected, output)

        url = 'https://raw.githubusercontent.com/tinybirdco/ecommerce_data_project_advanced/main/datasources/fixtures/events2.csv'
        output = await self._tb(["datasource", "replace", "events_replaced", f"{url}"])

        expected = [
            FeedbackManager.info_starting_import_process(),
            FeedbackManager.success_progress_blocks(),
            FeedbackManager.success_replaced_datasource(datasource='events_replaced'),
            FeedbackManager.info_data_pushed(datasource='events_replaced')
        ]

        self._assert_feedback_output(expected, output)
        output = await self._tb(["sql", "SELECT count() AS c FROM events_replaced", "--format", "JSON"])
        self.assertTrue(json.loads(output)['data'][0]['c'] == 3, f"Failed count with {output}")

    @tornado.testing.gen_test
    async def test_replace__should_replace_with_condition_from_file(self) -> None:
        await self._auth()

        file = self._get_resource_path('sales_replace.datasource')
        output = await self._tb(["push", file])

        file = self._get_fixture_path('sales_replace.csv')
        output = await self._tb(["datasource", "append", "sales_replace", file])
        expected = [
            FeedbackManager.info_starting_import_process(),
            FeedbackManager.success_progress_blocks(),
            FeedbackManager.success_total_rows(datasource='sales_replace', total_rows=2),
            FeedbackManager.success_appended_datasource(datasource='sales_replace'),
            FeedbackManager.info_data_pushed(datasource='sales_replace')
        ]

        self._assert_feedback_output(expected, output)
        output = await self._tb(["sql", "SELECT count() AS c FROM sales_replace", "--format", "JSON"])
        try:
            self.assertTrue(json.loads(output)['data'][0]['c'] == 2, f"Failed count with {output}")
        except json.JSONDecodeError:
            self.assertTrue(False, f"Invalid JSON: {output}")

        file = self._get_fixture_path('sales_replace2.csv')
        output = await self._tb(["datasource", "replace", "sales_replace", file, "--sql-condition", "toDate(local_timeplaced)=toDate('2019-01-01')"])
        expected = [
            FeedbackManager.info_starting_import_process(),
            FeedbackManager.success_progress_blocks(),
            FeedbackManager.success_replaced_datasource(datasource='sales_replace'),
            FeedbackManager.info_data_pushed(datasource='sales_replace')
        ]

        self._assert_feedback_output(expected, output)

        output = await self._tb(["sql", "SELECT count() AS c FROM sales_replace", "--format", "JSON"])
        self.assertTrue(json.loads(output)['data'][0]['c'] == 3, f"Failed count with {output}")

    @tornado.testing.gen_test
    async def test_replace__complete_replace_fails_on_if_called_with_parameters(self) -> None:
        await self._auth()

        file = self._get_resource_path('sales_replace.datasource')
        await self._tb(["push", file])

        file = self._get_fixture_path('sales_replace.csv')
        output = await self._tb(["datasource", "append", "sales_replace", file])
        self._assert_feedback_output([
            FeedbackManager.info_starting_import_process(),
            FeedbackManager.success_progress_blocks(),
            FeedbackManager.success_total_rows(datasource='sales_replace', total_rows=2),
            FeedbackManager.success_appended_datasource(datasource='sales_replace'),
            FeedbackManager.info_data_pushed(datasource='sales_replace')
        ], output)

        output = await self._tb(["datasource", "replace", "sales_replace", file, "--skip-incompatible-partition-key"])
        self._assert_feedback_output([
            FeedbackManager.info_starting_import_process(),
            FeedbackManager.error_operation_can_not_be_performed(error="Replace of complete Data Sources doesn't support replace options: skip_incompatible_partition_key.")
        ], output)


class TestCLIDatasourceGenerate(TestCLI):
    @tornado.testing.gen_test
    async def test_generate__should_generate_datasource_from_url_csv(self) -> None:
        await self._auth()

        url = 'https://storage.googleapis.com/tinybird-demo/stock_prices_800K.csv'
        stem = 'stock_prices_800K'
        output = await self._tb(["datasource", "generate", f"{url}"])
        expected = [FeedbackManager.success_generated_file(file=f'{stem}.datasource', stem=stem, filename=url)]
        self._assert_feedback_output(expected, output)

        with open(f'{self.CLI_PROJECT_PATH}{stem}.datasource') as f:
            lines = f.readlines()
            output = """DESCRIPTION >\n    Generated from https://storage.googleapis.com/tinybird-demo/stock_prices_800K.csv

SCHEMA >
    `symbol` String,
    `date` Date,
    `open` Float32,
    `high` Float32,
    `low` Float32,
    `close` Float32,
    `close_adjusted` Float32,
    `volume` Int64,
    `split_coefficient` Float32"""

            self.assertEqual(''.join(lines), output)

    @tornado.testing.gen_test
    async def test_generate__should_generate_datasource_from_url_csv_with_force_false(self) -> None:
        await self._auth()
        url = f'{HTTP_ADDRESS}/stock_prices_800K.csv'
        stem = 'stock_prices_800K'
        await self._tb(["datasource", "generate", f"{url}"])
        output = await self._tb(["datasource", "generate", f"{url}"])
        expected = [FeedbackManager.error_file_already_exists(file=f'{stem}.datasource')]
        self._assert_feedback_output(expected, output)

        with open(f'{self.CLI_PROJECT_PATH}{stem}.datasource') as f:
            lines = f.readlines()
            output = f"""DESCRIPTION >\n    Generated from {url}

SCHEMA >
    `symbol` String,
    `date` Date,
    `open` Float32,
    `high` Float32,
    `low` Float32,
    `close` Float32,
    `close_adjusted` Float32,
    `volume` Int64,
    `split_coefficient` Float32"""

            self.assertEqual(''.join(lines), output)

    @tornado.testing.gen_test
    async def test_generate__should_generate_datasource_from_url_csv_with_force(self) -> None:
        await self._auth()

        url = 'https://storage.googleapis.com/tinybird-demo/stock_prices_800K.csv'
        stem = 'stock_prices_800K'
        await self._tb(["datasource", "generate", f"{url}"])
        output = await self._tb(["datasource", "generate", f"{url}", "--force"])
        expected = [FeedbackManager.success_generated_file(file=f'{stem}.datasource', stem=stem, filename=url)]
        self._assert_feedback_output(expected, output)

        with open(f'{self.CLI_PROJECT_PATH}{stem}.datasource') as f:
            lines = f.readlines()
            output = """DESCRIPTION >\n    Generated from https://storage.googleapis.com/tinybird-demo/stock_prices_800K.csv

SCHEMA >
    `symbol` String,
    `date` Date,
    `open` Float32,
    `high` Float32,
    `low` Float32,
    `close` Float32,
    `close_adjusted` Float32,
    `volume` Int64,
    `split_coefficient` Float32"""

            self.assertEqual(''.join(lines), output)

    @tornado.testing.gen_test
    async def test_generate__should_generate_datasource_from_file_csv(self) -> None:
        await self._auth()

        file = self._get_resource_path('fixtures/sales_new.csv')
        stem = 'sales_new'
        output = await self._tb(["datasource", "generate", f"{file}"])
        expected = [FeedbackManager.success_generated_file(file=f'{stem}.datasource', stem=stem, filename=file)]
        self._assert_feedback_output(expected, output)

        with open(f'{self.CLI_PROJECT_PATH}{stem}.datasource') as f:
            lines = f.readlines()
            output = f"""DESCRIPTION >\n    Generated from {file}

SCHEMA >
    `cod_brand` Int16,
    `local_timeplaced` DateTime,
    `country` String,
    `purchase_location` Int16"""

            self.assertEqual(''.join(lines), output)

    @tornado.testing.gen_test
    async def test_generate__should_generate_datasource_from_file_ndjson(self) -> None:
        await self._auth()

        file = self._get_resource_path('fixtures/events.ndjson')
        stem = 'events'
        output = await self._tb(["datasource", "generate", f"{file}"])
        expected = [FeedbackManager.success_generated_file(file=f'{stem}.datasource', stem=stem, filename=file)]
        self._assert_feedback_output(expected, output)

        with open(f'{self.CLI_PROJECT_PATH}{stem}.datasource') as f:
            lines = f.readlines()
            output = f"""DESCRIPTION >\n    Generated from {file}

SCHEMA >
    date DateTime `json:$.date`,
    event String `json:$.event`,
    extra_data_city String `json:$.extra_data.city`,
    product_id String `json:$.product_id`,
    user_id Int32 `json:$.user_id`,
    extra_data_price Nullable(Float32) `json:$.extra_data.price`,
    extra_data_term Nullable(String) `json:$.extra_data.term`"""

            self.assertEqual(''.join(lines), output)

    @tornado.testing.gen_test
    async def test_generate__should_generate_datasource_from_url_ndjson(self) -> None:
        await self._auth()

        url = f'{HTTP_ADDRESS}/events.ndjson'
        stem = 'events'
        output = await self._tb(["datasource", "generate", f"{url}", "--force"])
        expected = [FeedbackManager.success_generated_file(file=f'{stem}.datasource', stem=stem, filename=url)]
        self._assert_feedback_output(expected, output)


class TestCLIDatasourceList(TestCLI):
    @tornado.testing.gen_test
    async def test_ls__should_return_all_the_datasources(self) -> None:
        await self._auth()
        output = await self._tb(["datasource", "ls"])
        self.assertTrue("test_table" in output)

    @tornado.testing.gen_test
    async def test_ls__should_return_all_the_datasources_in_format_json(self) -> None:
        await self._auth()
        output = await self._tb(["datasource", "ls", "--format", "json"])
        output_as_json = json.loads(output)
        self.assertEquals(output_as_json, {
            'datasources': [
                {
                    'prefix': '',
                    'version': '',
                    'shared from': '',
                    'name': 'test_table',
                    'row_count': unittest.mock.ANY,
                    'size': unittest.mock.ANY,
                    'created at': matches(r'2\d+-\d+-\d+ \d+:\d+:\d+'),
                    'updated at': matches(r'2\d+-\d+-\d+ \d+:\d+:\d+'),
                    'connection': ''
                }
            ]})


class TestCLIDatasourceRemove(TestCLI):
    @tornado.testing.gen_test
    async def test_rm__should_remove_a_datasource_if_exists(self) -> None:
        await self._auth()
        output = await self._tb(["datasource", "rm", "test_table"], "y")
        self.assertTrue("test_table" in output)
        self.assertTrue("Error" not in output)

    @tornado.testing.gen_test
    async def test_rm__should_not_remove_datasource_with_dependent_mvs(self) -> None:
        await self._auth()
        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        datasource_file.write("""
VERSION 0

SCHEMA >
    `id` UInt32,
    `views` UInt64

ENGINE "MergeTree"
            """)
        datasource_file.seek(0)
        output = await self._tb(["push", datasource_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=datasource_name, version='(v0)'),
            FeedbackManager.success_create(name=f"{datasource_name}__v0")
        ]
        self._assert_feedback_output(expected, output)

        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe')
        pipe_file.write(f"""
VERSION 0

NODE mt
SQL >
    SELECT toUInt32(a) as id, toUInt32(a * 100) as views FROM test_table

TYPE MATERIALIZED
DATASOURCE {datasource_name}
            """)
        pipe_file.seek(0)
        output = await self._tb(["push", pipe_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=pipe_name, version='(v0)'),
            FeedbackManager.success_create(name=f"{pipe_name}__v0")
        ]
        self._assert_feedback_output(expected, output)

        output = await self._tb(["datasource", "rm", "test_table"], "y", assert_exit_code=1)
        self.assertTrue("Error: ** test_table cannot be deleted:** " in output)
        self.assertTrue("Affected downstream materializations =>" in output)

        output = await self._tb(["datasource", "rm", f"{datasource_name}__v0"], "y")
        # Note: if we want this to be shown in the message, it shouldn't be through the error, we should revisit this
        # self.assertTrue("Affected upstream materializations =>" in output)
        self.assertTrue(f"Data Source '{datasource_name}__v0' deleted" in output)


class TestCLIDatasourceDeleteRows(TestCLI):
    @tornado.testing.gen_test
    async def test_rm__delete_rows_without_sql_condition_should_fail(self) -> None:
        await self._auth()
        output = await self._tb(["datasource", "delete", "test_table"], "y", assert_exit_code=2)
        self.assertTrue("Error" in output and "Missing option '--sql-condition'" in output, output)

    @tornado.testing.gen_test
    async def test_rm__delete_rows_with_empty_sql_condition_should_fail(self) -> None:
        await self._auth()
        output = await self._tb(["datasource", "delete", "test_table", "--sql-condition"], "y",
                                assert_exit_code=2)
        self.assertTrue("Error" in output and "Option '--sql-condition' requires an argument" in output)
        await self._auth()
        datasource = "mec"
        delete_condition = 'mec=3'
        output = await self._tb(["datasource", "delete", datasource, "--sql-condition", delete_condition], "y",
                                assert_exit_code=1)
        self.assertTrue("Error" in output and "\"mec\" does not exist" in output)
        expected = [
            FeedbackManager.warning_confirm_delete_rows_datasource(datasource=datasource, delete_condition=delete_condition)
        ]
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_rm__delete_rows_with_condition_returns_job_url(self) -> None:
        await self._auth()
        datasource = 'test_ds_a_good'
        file = self._get_resource_path(f'{datasource}.datasource')
        output = await self._tb(["push", file])
        delete_condition = 'a1=2'
        output = await self._tb(["datasource", "delete", datasource, "--sql-condition", delete_condition], "y")
        self.assertTrue("job url" in output and "/jobs/" in output)
        expected = [
            FeedbackManager.warning_confirm_delete_rows_datasource(datasource=datasource, delete_condition=delete_condition)
        ]
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_rm__delete_rows_with_condition_succeeds(self) -> None:
        await self._auth()
        datasource = 'test_ds_a_good'
        file = self._get_resource_path(f'{datasource}.datasource')
        await self._tb(["push", file])
        try:
            delete_condition = 'a1=2 or a2=\'mec\''
            output = await self._tb(["datasource", "delete", datasource, "--sql-condition", delete_condition, '--wait'], "y")
            self.assertTrue("job url" in output and "/jobs/" in output)
            self.assertTrue("Waiting for the job to finish" in output)
            expected = [
                FeedbackManager.warning_confirm_delete_rows_datasource(datasource=datasource, delete_condition=delete_condition),
                FeedbackManager.success_delete_rows_datasource(datasource=datasource, delete_condition=delete_condition)
            ]
            self._assert_feedback_output(expected, output)
        finally:
            output = await self._tb(["datasource", "rm", datasource], 'y')
            self.assertTrue('deleted' in output)

    @tornado.testing.gen_test
    async def test_rm__delete_rows_with_wrong_condition_fails(self) -> None:
        await self._auth()
        datasource = 'test_ds_a_good'
        file = self._get_resource_path(f'{datasource}.datasource')
        await self._tb(["push", file])
        try:
            delete_condition = 'z=test'
            output = await self._tb(["datasource", "delete", datasource, "--sql-condition", delete_condition, '--wait'], "y")
            self.assertTrue("job url" in output and "/jobs/" in output)
            self.assertTrue("Waiting for the job to finish" in output)
            self.assertTrue('Error' in output and "Missing columns:" in output, output)
        finally:
            output = await self._tb(["datasource", "rm", datasource], 'y')
            self.assertTrue('deleted' in output, output)


class TestCLIDatasourceShare(TestCLI):

    @tornado.testing.gen_test
    async def test_share_datasource(self) -> None:
        await self._auth()

        datasource_name = 'test_ds_a_good'
        file = self._get_resource_path(f'{datasource_name}.datasource')
        await self._tb(["push", file])

        extra_workspace_name, extra_workspace_token = await self._create_extra_workspace()

        output = await self._tb(["datasource", "share", f"{datasource_name}", extra_workspace_name, "--user_token", self.user_token, "--yes"])
        self._assert_feedback_output([
            f"The Data Source {datasource_name} has been correctly shared with {extra_workspace_name}"
        ], output)

        output = await self._tb(["datasource", "ls"], env={'TB_TOKEN': extra_workspace_token})
        self._assert_feedback_output([datasource_name], output)

    @tornado.testing.gen_test
    async def test_unshare_datasource(self) -> None:
        await self._auth()

        datasource_name = 'test_ds_a_good'
        file = self._get_resource_path(f'{datasource_name}.datasource')
        await self._tb(["push", file])

        extra_workspace_name, extra_workspace_token = await self._create_extra_workspace()

        # First share the DS
        output = await self._tb(["datasource", "share", f"{datasource_name}", extra_workspace_name, "--user_token", self.user_token, "--yes"])
        self._assert_feedback_output([
            f"The Data Source {datasource_name} has been correctly shared with {extra_workspace_name}"
        ], output)

        output = await self._tb(["datasource", "ls"], env={'TB_TOKEN': extra_workspace_token})
        self._assert_feedback_output([datasource_name], output)

        # Now unshare it
        output = await self._tb(["datasource", "unshare", f"{datasource_name}", extra_workspace_name, "--user_token", self.user_token, "--yes"])
        self._assert_feedback_output([
            f"The Data Source {datasource_name} has been correctly unshared from {extra_workspace_name}"
        ], output)

        output = await self._tb(["datasource", "ls"], env={'TB_TOKEN': extra_workspace_token})
        self._assert_feedback_output("---Empty---", output)

    @tornado.testing.gen_test
    async def test_share_datasource_that_not_exists(self) -> None:
        await self._auth()

        workspace_to_create = f"whatever_{uuid.uuid4().hex}"
        output = await self._tb(["workspace", "create", "--user_token", self.user_token, workspace_to_create])
        self._assert_feedback_output([
            workspace_to_create,
            "created"
        ], output)

        self.workspaces_to_delete.append(Users.get_by_name(workspace_to_create))

        output = await self._tb(["datasource", "share", "not_exists_datasource", workspace_to_create, "--user_token", self.user_token, "--yes"],
                                assert_exit_code=1)
        self._assert_feedback_output([
            FeedbackManager.error_datasource_does_not_exist(datasource="not_exists_datasource")
        ], output)

        output = await self._tb(["workspace", "delete", "--user_token", self.user_token, workspace_to_create, "--yes"])

        self._assert_feedback_output([
            workspace_to_create,
            "deleted"
        ], output)


class TestCLIDropPrefix(TestCLI):
    @tornado.testing.gen_test
    async def test_drop_prefix(self) -> None:
        await self._auth()

        name = 'test_ds_a_good'
        file = self._get_resource_path(f'drop-prefix/{name}.datasource')
        await self._tb(["push", file, '--prefix', 'ddd'])

        ds_name = 'test_ds_mat'
        file = self._get_resource_path(f'drop-prefix/{ds_name}.datasource')
        await self._tb(["push", file, '--prefix', 'ddd'])

        pipe_name = 'test_pipe_populate'
        file = self._get_resource_path(f'drop-prefix/{pipe_name}.pipe')
        await self._tb(["push", file, '--prefix', 'ddd'])

        expected = [
            FeedbackManager.info_removing_pipe(pipe=f'ddd__{pipe_name}'),
            FeedbackManager.info_removing_datasource(datasource=f'ddd__{ds_name}'),
            FeedbackManager.info_removing_datasource(datasource=f'ddd__{name}')
        ]

        # we need a separate directory to avoid parsing wrong files
        os.chdir(f'{os.path.dirname(__file__)}/cli/drop-prefix')
        output = await self._tb(['--token', self.admin_token, '--host', self.host, "drop-prefix", 'ddd', '--yes'])

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_drop_prefix_no_confirmation(self) -> None:
        await self._auth()

        name = 'test_ds_a_good'
        file = self._get_resource_path(f'drop-prefix/{name}.datasource')
        await self._tb(["push", file, '--prefix', 'ddd'])

        ds_name = 'test_ds_mat'
        file = self._get_resource_path(f'drop-prefix/{ds_name}.datasource')
        await self._tb(["push", file, '--prefix', 'ddd'])

        pipe_name = 'test_pipe_populate'
        file = self._get_resource_path(f'drop-prefix/{pipe_name}.pipe')
        await self._tb(["push", file, '--prefix', 'ddd'])

        expected = [
            FeedbackManager.warning_confirm_drop_prefix(prefix='ddd')
        ]

        # we need a separate directory to avoid parsing wrong files
        os.chdir(f'{os.path.dirname(__file__)}/cli/drop-prefix')
        output = await self._tb(['--token', self.admin_token, '--host', self.host, "drop-prefix", 'ddd'])

        self._assert_feedback_output(expected, output)


class TestCLIClearAll(TestCLI):
    @tornado.testing.gen_test
    async def test_clear_all(self) -> None:
        await self._auth()

        name = 'test_ds_a_good'
        file = self._get_resource_path(f'drop-prefix/{name}.datasource')
        await self._tb(["push", file])

        ds_name = 'test_ds_mat'
        file = self._get_resource_path(f'drop-prefix/{ds_name}.datasource')
        await self._tb(["push", file])

        pipe_name = 'test_pipe_populate'
        file = self._get_resource_path(f'drop-prefix/{pipe_name}.pipe')
        await self._tb(["push", file])

        expected = [
            FeedbackManager.info_removing_pipe(pipe=f'{pipe_name}'),
            FeedbackManager.info_removing_datasource(datasource=f'{ds_name}'),
            FeedbackManager.info_removing_datasource(datasource=f'{name}')
        ]

        # we need a separate directory to avoid parsing wrong files
        os.chdir(f'{os.path.dirname(__file__)}/cli/drop-prefix')
        output = await self._tb(['--token', self.admin_token, '--host', self.host, "workspace", "clear", '--yes'])

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_clear_all_no_confirmation(self) -> None:
        await self._auth()

        name = 'test_ds_a_good'
        file = self._get_resource_path(f'drop-prefix/{name}.datasource')
        await self._tb(["push", file])

        ds_name = 'test_ds_mat'
        file = self._get_resource_path(f'drop-prefix/{ds_name}.datasource')
        await self._tb(["push", file])

        pipe_name = 'test_pipe_populate'
        file = self._get_resource_path(f'drop-prefix/{pipe_name}.pipe')
        await self._tb(["push", file])

        expected = [
            FeedbackManager.warning_confirm_clear_workspace()
        ]

        # we need a separate directory to avoid parsing wrong files
        os.chdir(f'{os.path.dirname(__file__)}/cli/drop-prefix')
        output = await self._tb(['--token', self.admin_token, '--host', self.host, "workspace", "clear"])

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_clear_all_yes(self) -> None:
        await self._auth()

        name = 'test_ds_a_good'
        file = self._get_resource_path(f'drop-prefix/{name}.datasource')
        await self._tb(["push", file])

        ds_name = 'test_ds_mat'
        file = self._get_resource_path(f'drop-prefix/{ds_name}.datasource')
        await self._tb(["push", file])

        pipe_name = 'test_pipe_populate'
        file = self._get_resource_path(f'drop-prefix/{pipe_name}.pipe')
        await self._tb(["push", file])

        await self._tb(['--token', self.admin_token, '--host', self.host, "workspace", "clear", "--yes"])

        blank_datasources = ['{  "datasources": []}']
        output = await self._tb(['--token', self.admin_token, '--host', self.host, "datasource", "ls", "--format", "json"])
        self._assert_feedback_output(blank_datasources, output)

        blank_pipes = ['{  "pipes": []}']
        output = await self._tb(['--token', self.admin_token, '--host', self.host, "pipe", "ls", "--format", "json"])
        self._assert_feedback_output(blank_pipes, output)


class TestCLIPipeList(TestCLI):
    @tornado.testing.gen_test
    async def test_ls__should_return_all_the_pipes(self) -> None:
        await self._auth()
        output = await self._tb(["pipe", "ls"])
        self.assertTrue(self.pipe_name in output)

    @tornado.testing.gen_test
    async def test_ls__should_return_all_the_pipes_in_format_json(self) -> None:
        await self._auth()
        output = await self._tb(["pipe", "ls", "--format", "json"])
        output_as_json = json.loads(output)
        self.assertEquals(output_as_json, {
            'pipes': [
                {
                    'prefix': '',
                    'version': '',
                    'name': self.pipe_name,
                    'published date': matches(r'2\d+-\d+-\d+ \d+:\d+:\d+'),
                    'nodes': 1
                }
            ]})


class TestCLIPipeStats(TestCLI):
    @tornado.testing.gen_test
    async def test_displaying_stats(self) -> None:
        await self._auth()
        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe')
        pipe_file.write("""
NODE endpoint
SQL >
    SELECT 1 as x
""")
        pipe_file.seek(0)
        output = await self._tb(["push", pipe_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.success_create(name=pipe_name)
        ]

        self._assert_feedback_output(expected, output)

        for _ in range(10):
            await self._tb(["pipe", "data", pipe_name])

        self.force_flush_of_span_records()
        self.wait_for_public_table_replication('pipe_stats')

        output = await self._tb(["pipe", "stats"])
        expected = [
            # We don't validate the lantency as it might change
            f'prefix:version:name:{pipe_name}requestcount:10errorcount:0avglatency:'
        ]

        self._assert_feedback_output(expected, self._clean_table(output))

    @tornado.testing.gen_test
    async def test_displaying_stats_in_json(self) -> None:
        await self._auth()
        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe')
        pipe_file.write("""
NODE endpoint
SQL >
    SELECT 1 as x
""")
        pipe_file.seek(0)
        output = await self._tb(["push", pipe_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.success_create(name=pipe_name)
        ]
        self._assert_feedback_output(expected, output)

        for _ in range(10):
            await self._tb(["pipe", "data", pipe_name])

        self.force_flush_of_span_records()
        self.wait_for_public_table_replication('pipe_stats')

        output = await self._tb(["pipe", "stats", "--format", "json"])
        pipe_info = json.loads(output)['pipes'][0]

        self.assertTrue(pipe_info['name'] == pipe_name, pipe_info)
        self.assertTrue(pipe_info['requests'] == 10, pipe_info)
        self.assertTrue(pipe_info['errors'] == 0, pipe_info)

    @tornado.testing.gen_test
    async def test_filtering_by_pipe_name(self) -> None:
        await self._auth()

        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe')
        pipe_file.write("""
NODE endpoint
SQL >
    SELECT 1 as x
""")
        pipe_file.seek(0)
        output = await self._tb(["push", pipe_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.success_create(name=pipe_name)
        ]
        self._assert_feedback_output(expected, output)

        for _ in range(10):
            await self._tb(["pipe", "data", pipe_name])

        self.force_flush_of_span_records()
        self.wait_for_public_table_replication('pipe_stats')

        output = await self._tb(["pipe", "stats", "not_existing", "--format", "json"])
        pipes_info = json.loads(output)['pipes']

        self.assertTrue(len(pipes_info) == 0, pipes_info)


class TestCLIPipeEndpoint(TestCLI):
    @tornado.testing.gen_test
    async def test_pipe_publish__should_publish_and_unpublish_an_endpoint(self) -> None:
        await self._auth()

        name = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file])

        name = 'test_pipe_multiple_nodes'
        file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", file])

        output = await self._tb(["pipe", "publish", name, "first_node"])
        expected = [
            FeedbackManager.success_node_published(pipe=name, host=self.host)
        ]
        self._assert_feedback_output(expected, output)

        output = await self._tb(["pipe", "unpublish", name])
        expected = [
            FeedbackManager.success_node_unpublished(pipe=name, host=self.host)
        ]
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_pipe_publish__should_not_publish_an_endpoint_on_materialized_pipe(self) -> None:
        with User.transaction(self.WORKSPACE_ID) as w:
            w.feature_flags[FeatureFlagWorkspaces.PIPE_ENDPOINT_RESTRICTIONS.value] = True

        await self._auth()
        datasource = 'test_ds_a_good'
        datasource_file = self._get_resource_path(f'{datasource}.datasource')
        await self._tb(["push", datasource_file])

        pipe = 'test_pipe_multiple_nodes'
        pipe_file = self._get_resource_path(f'{pipe}.pipe')

        output = await self._tb(['materialize', pipe_file])

        output = await self._tb(["pipe", "publish", pipe, "second_node"], assert_exit_code=1)
        expected = [
            'Error: ** Forbidden: Pipe test_pipe_multiple_nodes cannot be an endpoint because it already has a materialized view.'
        ]
        self._assert_feedback_output(expected, output)

        with User.transaction(self.WORKSPACE_ID) as w:
            w.feature_flags[FeatureFlagWorkspaces.PIPE_ENDPOINT_RESTRICTIONS.value] = False

    @tornado.testing.gen_test
    async def test_pipe_push_publishes_endpoint(self) -> None:
        await self._auth()
        ds_name = 'test_ds_a_good'
        ds_file = self._get_resource_path(f'{ds_name}.datasource')
        output = await self._tb(["push", ds_file])
        pipe_name = 'test_pipe_multiple_nodes'
        pipe_file = self._get_resource_path(f'{pipe_name}.pipe')

        # a simple push publishes the last node as the endpoint
        output = await self._tb(["push", pipe_file])
        expected = [
            FeedbackManager.success_test_endpoint_no_token(pipe=pipe_name, host=self.host)
        ]
        self._assert_feedback_output(expected, output)
        await self.check_endpoint_name(pipe_name, 'second_node')

        # changes the endpoint to the first node
        output = await self._tb(["pipe", "publish", pipe_name, "first_node"])
        expected = [
            FeedbackManager.success_node_published(pipe=pipe_name, host=self.host)
        ]
        self._assert_feedback_output(expected, output)
        await self.check_endpoint_name(pipe_name, 'first_node')

        # repushing the pipe, should maintain whatever endpoint was set, in this case, first_node
        await self._tb(["push", pipe_file, "--force"])
        await self.check_endpoint_name(pipe_name, 'first_node')

    @tornado.testing.gen_test
    async def test_pipe_with_renamed_endpoint_publishes_last_node(self) -> None:
        await self._auth()
        ds_name = 'test_ds_a_good'
        ds_file = self._get_resource_path(f'{ds_name}.datasource')
        output = await self._tb(["push", ds_file])

        # a simple push publishes the last node as the endpoint
        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe')
        pipe_file.write("""
NODE node_0
SQL >
    SELECT * FROM test_ds_a_good

NODE node_1
SQL >
    SELECT * FROM node_0
            """)
        pipe_file.seek(0)
        output = await self._tb(["push", pipe_file.name])
        expected = [
            FeedbackManager.success_test_endpoint_no_token(pipe=pipe_name, host=self.host)
        ]
        self._assert_feedback_output(expected, output)
        await self.check_endpoint_name(pipe_name, 'node_1')

        # changes the endpoint to the first node
        output = await self._tb(["pipe", "publish", pipe_name, "node_0"])
        expected = [
            FeedbackManager.success_node_published(pipe=pipe_name, host=self.host)
        ]
        self._assert_feedback_output(expected, output)
        await self.check_endpoint_name(pipe_name, 'node_0')

        # renames the first node, so the second node becomes the endpoint
        pipe_file.write("""
NODE node_renamed
SQL >
    SELECT * FROM test_ds_a_good

NODE node_1
SQL >
    SELECT * FROM node_renamed
            """)
        pipe_file.seek(0)
        await self._tb(["push", pipe_file.name, "--force"])
        await self.check_endpoint_name(pipe_name, 'node_1')


class TestCLIPipePopulate(TestCLI):
    @tornado.testing.gen_test
    async def test_pipe_populate__happy_case(self) -> None:
        await self._auth()

        ds_source_name = 'test_ds_a_good'
        ds_source_file = self._get_resource_path(f'{ds_source_name}.datasource')
        output = await self._tb(["push", ds_source_file])

        ds_target_name = 'test_ds_mat'
        ds_target_file = self._get_resource_path(f'{ds_target_name}.datasource')
        await self._tb(["push", ds_target_file])

        pipe_name = 'test_pipe_populate'
        file = self._get_resource_path(f'{pipe_name}.pipe')
        output = await self._tb(["push", file, "--populate", "--wait"])

        expected = [
            f'** Warning: {ds_source_name} not found inside:',
            f'** Warning: {ds_target_name} not found inside:',
            FeedbackManager.info_materialized_datasource_used(pipe=pipe_name, datasource=ds_target_name),
            FeedbackManager.info_populate_job_url(url=f'http://localhost:{self.app.settings["port"]}/v0/jobs/'),
            FeedbackManager.success_create(name=pipe_name)
        ]

        self._assert_feedback_output(expected, output)

        # Force populate must also work if only one of the datasource files is not found
        shutil.copy(ds_target_file, '.')  # copy target datasource file to working directory, so checks can find it
        output = await self._tb(["push", file, "--populate", "--wait", "--force"])
        self._assert_feedback_output([f'** Warning: {ds_target_name} not found inside:'], output, not_in=True)
        os.remove(f'{ds_target_name}.datasource')
        shutil.copy(ds_source_file, '.')
        output = await self._tb(["push", file, "--populate", "--wait", "--force"])
        self._assert_feedback_output([f'** Warning: {ds_source_name} not found inside:'], output, not_in=True)

    @tornado.testing.gen_test
    @patch.object(Job, 'mark_as_working', side_effect=CHException('mock error on populate'))
    async def test_pipe_populate__unlink_if_error(self, _mock):
        await self._auth()

        name = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file])

        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        datasource_file.write("""
SCHEMA >
    `m1` Int64,
    `m2` String,
    `m3` String

ENGINE "MergeTree"
ENGINE_PARTITION_KEY "m1"
ENGINE_SORTING_KEY "m1"
            """)

        datasource_file.seek(0)
        await self._tb(["push", datasource_file.name])

        (pipe_file, _) = self.create_tmp_file(suffix='.pipe')
        pipe_file.write(f"""
NODE mv
SQL >

    SELECT
        a1 as m1,
        a2 as m2,
        a3 as m3
    FROM test_ds_a_good

TYPE materialized
DATASOURCE {datasource_name}
            """)

        pipe_file.seek(0)
        output = await self._tb(["push", pipe_file.name, "--force", "--populate", "--wait"], assert_exit_code=1)
        error = "mock error on populate: the Materialized View has been unlinked and it's not materializing data. Fix the issue in the Materialized View and create it again."
        self.assertTrue(error in output)

    @patch('tinybird.client.TinyB.wait_for_job', side_effect=Exception('error getting job'))
    @tornado.testing.gen_test
    async def test_pipe_populate__error_getting_job(self, _mock):
        await self._auth()

        name = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file])

        ds_name = 'test_ds_mat'
        file = self._get_resource_path(f'{ds_name}.datasource')
        await self._tb(["push", file])

        pipe_name = 'test_pipe_populate'
        file = self._get_resource_path(f'{pipe_name}.pipe')
        output = await self._tb(["push", file, "--populate", "--wait"], assert_exit_code=1)
        expected = ["Error while getting job status:\nerror getting job"]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_pipe_populate_subset__happy_case(self) -> None:
        await self._auth()

        name = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file])

        ds_name = 'test_ds_mat'
        file = self._get_resource_path(f'{ds_name}.datasource')
        await self._tb(["push", file])

        pipe_name = 'test_pipe_populate'
        file = self._get_resource_path(f'{pipe_name}.pipe')
        output = await self._tb(["push", file, "--populate", "--wait", "--subset=0.1"])

        expected = [
            FeedbackManager.info_materialized_datasource_used(pipe=pipe_name, datasource=ds_name),
            FeedbackManager.info_populate_subset_job_url(url=f'http://localhost:{self.app.settings["port"]}/v0/jobs/', subset='0.1'),
            FeedbackManager.success_create(name=pipe_name)
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_pipe_populate_condition__happy_case(self) -> None:
        await self._auth()

        name = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file])

        ds_name = 'test_ds_mat'
        file = self._get_resource_path(f'{ds_name}.datasource')
        await self._tb(["push", file])

        pipe_name = 'test_pipe_populate'
        file = self._get_resource_path(f'{pipe_name}.pipe')
        output = await self._tb(["push", file, "--populate", "--wait", "--sql-condition", "1=1"])

        expected = [
            FeedbackManager.info_materialized_datasource_used(pipe=pipe_name, datasource=ds_name),
            FeedbackManager.info_populate_condition_job_url(url=f'http://localhost:{self.app.settings["port"]}/v0/jobs/', populate_condition='1=1'),
            FeedbackManager.success_create(name=pipe_name)
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_pipe_populate_subset__error(self) -> None:
        await self._auth()

        name = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file])

        ds_name = 'test_ds_mat'
        file = self._get_resource_path(f'{ds_name}.datasource')
        await self._tb(["push", file])

        pipe_name = 'test_pipe_populate'
        file = self._get_resource_path(f'{pipe_name}.pipe')
        output = await self._tb(["push", file, "--populate", "--wait", "--subset=2"], assert_exit_code=1)

        assert ('"--subset" must be a decimal number > 0 and <= 1' in output) is True

    @tornado.testing.gen_test
    async def test_pipe_populate_condition__error(self) -> None:
        await self._auth()

        name = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file])

        ds_name = 'test_ds_mat'
        file = self._get_resource_path(f'{ds_name}.datasource')
        await self._tb(["push", file])

        pipe_name = 'test_pipe_populate'
        file = self._get_resource_path(f'{pipe_name}.pipe')

        output = await self._tb(["push", file, "--populate", "--wait", "--sql-condition", "not valid condition"], assert_exit_code=1)

        assert ('Cannot apply SQL condition' in output) is True

        output = await self._tb(["push", file, "--populate", "--force", "--wait", "--sql-condition='1=1'"], assert_exit_code=1)
        assert ("Cannot apply SQL condition" in output) is True

    @tornado.testing.gen_test
    async def test_pipe_populate_wait__happy_case(self) -> None:
        await self._auth()

        name = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file])

        ds_name = 'test_ds_mat'
        file = self._get_resource_path(f'{ds_name}.datasource')
        await self._tb(["push", file])

        pipe_name = 'test_pipe_populate'
        file = self._get_resource_path(f'{pipe_name}.pipe')
        output = await self._tb(["push", file, "--populate", "--wait"])

        expected = [
            FeedbackManager.info_materialized_datasource_used(pipe=pipe_name, datasource=ds_name),
            FeedbackManager.info_populate_job_url(url=f'http://localhost:{self.app.settings["port"]}/v0/jobs/'),
            FeedbackManager.success_create(name=pipe_name),
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_pipe_populate__matview_error(self) -> None:
        await self._auth()

        name = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file])

        ds_name = 'test_ds_mat'
        file = self._get_resource_path(f'{ds_name}.datasource')
        await self._tb(["push", file])

        pipe_name = 'test_pipe_populate_bad'
        file = self._get_resource_path(f'{pipe_name}.pipe')
        output = await self._tb(["push", file, "--populate", "--wait"], assert_exit_code=1)

        expected = [
            FeedbackManager.error_while_check_materialized(
                error="Cannot materialize node: The pipe has columns ['a1'] not found in the destination Data Source")
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_populate_is_being_track_using_query_log(self) -> None:
        await self._auth()

        real_query_sync = HTTPClient.query_sync

        def fake_query_sync(self, *args, **kwargs):
            result = real_query_sync(self, *args, **kwargs)
            if kwargs.get('user_agent', '') == 'no-tb-populate-query':
                raise CHException(f"Code: {CHErrors.TIMEOUT_EXCEEDED}, e.displayText() = DB::Exception: Timeout exceeded: elapsed 10 seconds", fatal=False)
            return result

        self.mpatch.setattr(HTTPClient, 'query_sync', fake_query_sync)

        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        datasource_file.write("""
SCHEMA >
    timestamp Datetime,
    purchase_location UInt16,
    units UInt32

ENGINE "MergeTree"
ENGINE_PARTITION_KEY ""
ENGINE_SORTING_KEY tuple()
            """)

        datasource_file.seek(0)
        output = await self._tb(["push", datasource_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=datasource_name, version=''),
            FeedbackManager.success_create(name=datasource_name)
        ]

        self._assert_feedback_output(expected, output)

        (endpoint_file, endpoint_name) = self.create_tmp_file(suffix='.pipe')
        endpoint_file.write("""
NODE endpoint
SQL >
    SELECT *
    FROM generateRandom('timestamp DateTime, purchase_location UInt16, units UInt32')
    LIMIT 1000
            """)

        endpoint_file.seek(0)
        output = await self._tb(["push", endpoint_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=endpoint_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=endpoint_name, version=''),
            FeedbackManager.success_create(name=endpoint_name)
        ]

        self._assert_feedback_output(expected, output)

        output = await self._tb(["datasource", "append", datasource_name, f"{self.host}/v0/pipes/{endpoint_name}.csv?token={self.admin_token}"])
        expected = [
            FeedbackManager.info_starting_import_process(),
            FeedbackManager.success_progress_blocks(),
            FeedbackManager.success_total_rows(datasource=datasource_name, total_rows=1000),
            FeedbackManager.success_appended_datasource(datasource=datasource_name),
            FeedbackManager.info_data_pushed(datasource=datasource_name)
        ]
        self._assert_feedback_output(expected, output)

        (mv_datasource_file, mv_datasource_name) = self.create_tmp_file(suffix='.datasource')
        mv_datasource_file.write("""
SCHEMA >
    date Date,
    purchase_location UInt16,
    units UInt64

ENGINE "SummingMergeTree"
ENGINE_PARTITION_KEY ""
ENGINE_SORTING_KEY "date, purchase_location"
            """)

        mv_datasource_file.seek(0)
        output = await self._tb(["push", mv_datasource_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=mv_datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=mv_datasource_name, version=''),
            FeedbackManager.success_create(name=mv_datasource_name)
        ]

        self._assert_feedback_output(expected, output)

        (mv_pipe_file, mv_pipe_name) = self.create_tmp_file(suffix='.pipe')
        mv_pipe_file.write(f"""
NODE endpoint
SQL >
    SELECT
        toDate(timestamp) as date,
        purchase_location,
        sum(units) as units
    FROM {datasource_name}
    GROUP BY date, purchase_location

TYPE MATERIALIZED
DATASOURCE {mv_datasource_name}
            """)

        mv_pipe_file.seek(0)
        output = await self._tb(["push", mv_pipe_file.name, "--populate", "--wait"])
        expected = [
            FeedbackManager.info_processing_file(filename=mv_pipe_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=mv_pipe_name, version=''),
            FeedbackManager.success_create(name=mv_pipe_name)
        ]
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_populate_is_being_track_using_query_log_on_cluster(self) -> None:

        await self._auth()

        real_query_sync = HTTPClient.query_sync

        def fake_query_sync(self, *args, **kwargs):
            result = real_query_sync(self, *args, **kwargs)
            if kwargs.get('user_agent', '') == 'no-tb-populate-query':
                raise CHException(f"Code: {CHErrors.TIMEOUT_EXCEEDED}, e.displayText() = DB::Exception: Timeout exceeded: elapsed 10 seconds", fatal=False)
            return result

        self.mpatch.setattr(HTTPClient, 'query_sync', fake_query_sync)

        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        datasource_file.write("""
SCHEMA >
    timestamp Datetime,
    purchase_location UInt16,
    units UInt32

ENGINE "MergeTree"
ENGINE_PARTITION_KEY ""
ENGINE_SORTING_KEY tuple()
            """)

        datasource_file.seek(0)
        output = await self._tb(["push", datasource_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=datasource_name, version=''),
            FeedbackManager.success_create(name=datasource_name)
        ]

        self._assert_feedback_output(expected, output)

        (endpoint_file, endpoint_name) = self.create_tmp_file(suffix='.pipe')
        endpoint_file.write("""
NODE endpoint
SQL >
    SELECT *
    FROM generateRandom('timestamp DateTime, purchase_location UInt16, units UInt32')
    LIMIT 1000
            """)

        endpoint_file.seek(0)
        output = await self._tb(["push", endpoint_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=endpoint_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=endpoint_name, version=''),
            FeedbackManager.success_create(name=endpoint_name)
        ]

        self._assert_feedback_output(expected, output)

        output = await self._tb(["datasource", "append", datasource_name, f"{self.host}/v0/pipes/{endpoint_name}.csv?token={self.admin_token}"])
        expected = [
            FeedbackManager.info_starting_import_process(),
            FeedbackManager.success_progress_blocks(),
            FeedbackManager.success_total_rows(datasource=datasource_name, total_rows=1000),
            FeedbackManager.success_appended_datasource(datasource=datasource_name),
            FeedbackManager.info_data_pushed(datasource=datasource_name)
        ]
        self._assert_feedback_output(expected, output)

        (mv_datasource_file, mv_datasource_name) = self.create_tmp_file(suffix='.datasource')
        mv_datasource_file.write("""
SCHEMA >
    date Date,
    purchase_location UInt16,
    units UInt64

ENGINE "SummingMergeTree"
ENGINE_PARTITION_KEY ""
ENGINE_SORTING_KEY "date, purchase_location"
            """)

        mv_datasource_file.seek(0)
        output = await self._tb(["push", mv_datasource_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=mv_datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=mv_datasource_name, version=''),
            FeedbackManager.success_create(name=mv_datasource_name)
        ]

        self._assert_feedback_output(expected, output)

        (mv_pipe_file, mv_pipe_name) = self.create_tmp_file(suffix='.pipe')
        mv_pipe_file.write(f"""
NODE endpoint
SQL >
    SELECT
        toDate(timestamp) as date,
        purchase_location,
        sum(units) as units
    FROM {datasource_name}
    GROUP BY date, purchase_location

TYPE MATERIALIZED
DATASOURCE {mv_datasource_name}
            """)

        mv_pipe_file.seek(0)
        output = await self._tb(["push", mv_pipe_file.name, "--populate", "--wait"])
        expected = [
            FeedbackManager.info_processing_file(filename=mv_pipe_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=mv_pipe_name, version=''),
            FeedbackManager.success_create(name=mv_pipe_name)
        ]
        self._assert_feedback_output(expected, output)


class TestCLIPipeCopy(TestCLI):
    @tornado.testing.gen_test
    async def test_pipe_copy__should_run_a_copy_job(self) -> None:
        with User.transaction(self.WORKSPACE_ID) as w:
            w.feature_flags[FeatureFlagWorkspaces.EXPORT.value] = True
        await self._auth()

        origin_ds_name = 'test_ds_a_good'
        origin_ds_file = self._get_resource_path(f'{origin_ds_name}.datasource')
        await self._tb(["push", origin_ds_file])

        (append_file, append_name) = self.create_tmp_file(suffix='.csv')
        append_file.write('1,test1,test2\n2,test3,test4')
        append_file.seek(0)
        await self._tb(["datasource", "append", origin_ds_name, append_file.name])

        target_ds_name = 'test_ds_a_good_with_description'
        target_ds_file = self._get_resource_path(f'{target_ds_name}.datasource')
        await self._tb(["push", target_ds_file])

        params = {'token': self.admin_token}

        response = await self.fetch_async(
            path=f'/v0/datasources/{target_ds_name}?{urlencode(params)}',
            method='GET')

        target_datasource = json.loads(response.body)
        initial_row_count = target_datasource['statistics']['row_count']

        pipe_name = 'test_pipe_copy'
        pipe_file = self._get_resource_path(f'{pipe_name}.pipe')
        await self._tb(["push", pipe_file])

        output = await self._tb(["pipe", "copy", pipe_name, "--yes", "--wait"])

        expected = [
            FeedbackManager.info_copy_job_running(pipe=pipe_name),
            FeedbackManager.success_copy_job_created(target_datasource=target_ds_name, job_id=''),
            FeedbackManager.success_data_copied_to_ds(target_datasource=target_ds_name)
        ]
        self._assert_feedback_output(expected, output)

        response = await self.fetch_async(
            path=f'/v0/datasources/{target_ds_name}?{urlencode(params)}',
            method='GET')

        target_datasource = json.loads(response.body)
        row_count = target_datasource['statistics']['row_count']

        assert initial_row_count == 0
        assert row_count == 2

        with User.transaction(self.WORKSPACE_ID) as w:
            w.feature_flags[FeatureFlagWorkspaces.EXPORT.value] = False

    @tornado.testing.gen_test
    async def test_pipe_copy__should_run_a_copy_job_with_params(self) -> None:
        with User.transaction(self.WORKSPACE_ID) as w:
            w.feature_flags[FeatureFlagWorkspaces.EXPORT.value] = True
        await self._auth()

        origin_ds_name = 'test_ds_a_good'
        origin_ds_file = self._get_resource_path(f'{origin_ds_name}.datasource')
        await self._tb(["push", origin_ds_file])

        (append_file, append_name) = self.create_tmp_file(suffix='.csv')
        append_file.write('1,test1,test2\n2,test3,test4')
        append_file.seek(0)
        await self._tb(["datasource", "append", origin_ds_name, append_file.name])

        target_ds_name = 'test_ds_a_good_with_description'
        target_ds_file = self._get_resource_path(f'{target_ds_name}.datasource')
        await self._tb(["push", target_ds_file])

        params = {'token': self.admin_token}

        response = await self.fetch_async(
            path=f'/v0/datasources/{target_ds_name}?{urlencode(params)}',
            method='GET')

        target_datasource = json.loads(response.body)
        initial_row_count = target_datasource['statistics']['row_count']

        pipe_name = 'test_pipe_copy_params'
        pipe_file = self._get_resource_path(f'{pipe_name}.pipe')
        await self._tb(["push", pipe_file])

        output = await self._tb(["pipe", "copy", pipe_name, "--yes", "--wait"])

        expected = [
            FeedbackManager.info_copy_job_running(pipe=pipe_name),
            FeedbackManager.success_copy_job_created(target_datasource=target_ds_name, job_id=''),
            FeedbackManager.success_data_copied_to_ds(target_datasource=target_ds_name)
        ]
        self._assert_feedback_output(expected, output)

        response = await self.fetch_async(
            path=f'/v0/datasources/{target_ds_name}?{urlencode(params)}',
            method='GET')

        target_datasource = json.loads(response.body)
        row_count = target_datasource['statistics']['row_count']

        assert initial_row_count == 0
        assert row_count == 1

        with User.transaction(self.WORKSPACE_ID) as w:
            w.feature_flags[FeatureFlagWorkspaces.EXPORT.value] = False


class TestCLIPipeRegressionTest(TestCLI):
    def setUp(self) -> None:
        super().setUp()
        self.app.settings["api_host"] = self.get_host()

    @tornado.testing.gen_test
    async def test_pipe_regression_test__happy_case(self) -> None:
        await self._auth()

        name = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file])

        name = 'test_pipe_a_good'
        file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", file])

        with tempfile.NamedTemporaryFile(suffix='.csv', mode='w+', encoding='utf-8') as append_file:
            append_file.write('1,test1,test2')
            append_file.seek(0)
            await self._tb(["datasource", "append", "test_ds_a_good", append_file.name])

        await self._tb(["pipe", "data", name])

        output = await self._tb(["pipe", "regression-test", file])

        expected = [
            FeedbackManager.info_processing_file(filename=file),
            FeedbackManager.info_building_dependencies(),
        ]
        self._assert_feedback_output(expected, output)

        unexpected = [
            FeedbackManager.success_create(name=name),
            FeedbackManager.info_not_pushing_fixtures(),
            'Test FAILED'
        ]
        self._assert_feedback_output(unexpected, output, not_in=True)

    @tornado.testing.gen_test
    async def test_pipe_regression_test__fail_regression_test(self) -> None:
        await self._auth()

        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        (append_file, append_name) = self.create_tmp_file(suffix='.csv')
        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe')

        datasource_file.write("""
SCHEMA >
`a1` Int64,
`a2` String,
`a3` String

ENGINE "MergeTree"
        """)
        datasource_file.seek(0)
        await self._tb(["push", datasource_file.name])

        append_file.write('1,test1,test2')
        append_file.seek(0)
        await self._tb(["datasource", "append", datasource_name, append_file.name])

        pipe_file.write(f"""
NODE mv
SQL >

    SELECT
        a1,
        a2,
        a3
    FROM {datasource_name}
            """)

        pipe_file.seek(0)
        await self._tb(["push", pipe_file.name])
        await self._tb(["pipe", "data", pipe_name])

        self.force_flush_of_span_records()
        self.wait_for_public_table_replication('pipe_stats_rt')

        pipe_file.write(f"""
NODE mv
SQL >

    SELECT
        2 as a1,
        a2,
        a3
    FROM {datasource_name}
            """)
        pipe_file.seek(0)
        output = await self._tb(["pipe", "regression-test", pipe_file.name],
                                assert_exit_code=1)

        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file.name),
            FeedbackManager.info_building_dependencies(),
            'Test FAILED'
        ]
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_pipe_regression_test_fail_fast(self) -> None:
        await self._auth()

        # Note that the datasource file uses a longer suffix to test the case where the datasource ends with __ which
        # was crashing before
        (datasource_file, datasource_name) = self.create_tmp_file(suffix='tmp6uun82__.datasource')
        (append_file, append_name) = self.create_tmp_file(suffix='.csv')
        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe')

        datasource_file.write("""
SCHEMA >
    `a1` Int64,
    `a2` String,
    `a3` String

ENGINE "MergeTree"
            """)
        datasource_file.seek(0)
        await self._tb(["push", datasource_file.name])

        append_file.write('1,test1,test2')
        append_file.seek(0)
        await self._tb(["datasource", "append", datasource_name, append_file.name])

        pipe_file.write(f"""
NODE mv
SQL >

    SELECT
        a1,
        a2,
        a3
    FROM {datasource_name}
""")

        pipe_file.seek(0)
        await self._tb(["push", pipe_file.name])
        await self._tb(["pipe", "data", pipe_name])
        await self._tb(["pipe", "data", pipe_name])

        self.force_flush_of_span_records()
        self.wait_for_public_table_replication('pipe_stats_rt')

        pipe_file.write(f"""
NODE mv
SQL >
    %
    SELECT
        2 as a1,
        a2,
        a3
    FROM {datasource_name}
""")
        pipe_file.seek(0)
        output = await self._tb(["pipe", "regression-test", pipe_file.name, "-ff"],
                                assert_exit_code=1)
        self.force_flush_of_span_records()
        self.wait_for_public_table_replication('pipe_stats_rt')

        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file.name),
            FeedbackManager.info_building_dependencies(),
            'Test FAILED'
        ]
        self._assert_feedback_output(expected, output)

        pipe_stats = await self._tb(["sql", f"SELECT count() as requests FROM tinybird.pipe_stats_rt WHERE url LIKE '%{pipe_name}.json%'", "--format", "json"])
        checker_stats = await self._tb(["sql", f"SELECT count() as requests FROM tinybird.pipe_stats_rt WHERE url LIKE '%{pipe_name}__checker%'", "--format", "json"])
        self.assertEqual(json.loads(checker_stats)['data'][0]['requests'], 3)
        self.assertEqual(json.loads(pipe_stats)['data'][0]['requests'], 5)

    @tornado.testing.gen_test
    async def test_pipe_regression_test_ignore_order(self) -> None:
        await self._auth()

        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        (append_file, append_name) = self.create_tmp_file(suffix='.csv')
        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe')

        datasource_file.write("""
SCHEMA >
`a1` Int64,
`a2` String,
`a3` String

ENGINE "MergeTree"
        """)
        datasource_file.seek(0)
        await self._tb(["push", datasource_file.name])

        append_file.write('1,test1,test2\n2,test3,test4')
        append_file.seek(0)
        await self._tb(["datasource", "append", datasource_name, append_file.name])

        pipe_file.write(f"""
NODE mv
SQL >

    SELECT
        a1,
        arraySort(x -> x, groupArray(a2)) as a2,
        arraySort(x -> x, groupArray(a3)) as a3
    FROM {datasource_name}
    GROUP BY a1
    ORDER BY a1 DESC
""")

        pipe_file.seek(0)
        await self._tb(["push", pipe_file.name])
        await self._tb(["pipe", "data", pipe_name])
        await self._tb(["pipe", "data", pipe_name])

        self.force_flush_of_span_records()

        pipe_file.write(f"""
    NODE mv
    SQL >
        %
        SELECT
            a1,
            arrayReverseSort(x -> x, groupArray(a2)) as a2,
            arrayReverseSort(x -> x, groupArray(a3)) as a3
        FROM {datasource_name}
        ORDER BY a1 ASC
    """)
        pipe_file.seek(0)
        output = await self._tb(["pipe", "regression-test", pipe_file.name, "--ignore-order"],
                                assert_exit_code=1)

        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file.name),
            FeedbackManager.info_building_dependencies(),
        ]
        self._assert_feedback_output(expected, output)
        expected = [
            'Test FAILED'
        ]
        self._assert_feedback_output(expected, output, not_in=True)

    @tornado.testing.gen_test
    async def test_ignore_order_with_null_values(self) -> None:
        await self._auth()

        (pipe_file, pipe_name) = self.create_tmp_file(suffix='.pipe')
        pipe_file.write("""
NODE endpoint
SQL >
    SELECT
        NULL as x,
        3 as y
    UNION ALL
    SELECT
        'Hello World' as x,
        4 as y
""")
        pipe_file.seek(0)
        output = await self._tb(["push", pipe_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.success_create(name=pipe_name)
        ]

        self._assert_feedback_output(expected, output)

        params = {
            'token': self.admin_token
        }
        response = await self.fetch_async(f'/v0/pipes/{pipe_name}.json?{urlencode(params)}')
        self.assertEqual(response.code, 200, response.body)
        self.force_flush_of_span_records()
        self.wait_for_public_table_replication('pipe_stats_rt')

        pipe_file.write("""
NODE endpoint
SQL >
    SELECT
        'Hello World' as x,
        4 as y
    UNION ALL
    SELECT
        NULL as x,
        3 as y
""")
        pipe_file.seek(0)
        self.force_flush_of_span_records()
        self.wait_for_public_table_replication('pipe_stats_rt')
        output = await self._tb(["pipe", "regression-test", pipe_file.name, "--ignore-order"])
        expected = [
            FeedbackManager.info_processing_file(filename=pipe_file.name),
            FeedbackManager.info_building_dependencies(),
            """
------------------------------------------------------------------------
| Test Run | Test Passed | Test Failed | % Test Passed | % Test Failed |
------------------------------------------------------------------------
|        1 |           1 |           0 |         100.0 |           0.0 |
------------------------------------------------------------------------
"""
        ]

        self._assert_feedback_output(expected, output)


class TestCLIPipeAppendNodeTest(TestCLI):

    @tornado.testing.gen_test
    async def test_append_node_to_pipe(self) -> None:
        await self._auth()
        output = await self._tb(["pipe", "append", self.pipe_name, f"SELECT * FROM {self.datasource_name}"])
        self.assertTrue("New node: " in output)
        self.assertTrue(self.pipe_name in output)

    @tornado.testing.gen_test
    async def test_append_node_pipe_doesnt_exist(self) -> None:
        await self._auth()
        unknown_pipe_name = "unknown_pipe"
        output = await self._tb(["pipe", "append", unknown_pipe_name, f"SELECT * FROM {self.datasource_name}"], assert_exit_code=1)
        expected = [FeedbackManager.error_pipe_does_not_exist(pipe=unknown_pipe_name)]
        self._assert_feedback_output(expected, output)


class TestCLIJobCancel(TestCLI):
    def setUp(self) -> None:
        super().setUp()

        self.main_workspace = Users.get_by_id(self.WORKSPACE_ID)
        self.main_workspace_token = Users.get_token_for_scope(self.main_workspace, scopes.DATASOURCES_CREATE)

        secondary_email = f'my_secondary_user_{uuid.uuid4().hex}@example.com'
        UserAccount.register(secondary_email, 'pass')
        self.secondary_user = UserAccount.get_by_email(secondary_email)
        self.secondary_user_token = UserAccount.get_token_for_scope(self.secondary_user, scopes.AUTH)

        self.secondary_workspace = self.register_workspace(f'my_secondary_ws_{uuid.uuid4().hex}', admin=self.secondary_user.id)
        self.secondary_workspace_token = UserAccount.get_token_for_scope(self.secondary_user, scopes.DATASOURCES_CREATE)

    def tearDown(self) -> None:
        UserAccount._delete(self.secondary_user.id)
        User._delete(self.secondary_workspace.id)

        super().tearDown()

    @tornado.testing.gen_test
    async def test_job_cancel__job_correctly_set_as_cancelled(self) -> None:
        await self._auth()

        job = await self._create_fake_job(self.job_executor, self.main_workspace)

        output = await self._tb(["job", "cancel", job.id])

        expected = [
            FeedbackManager.success_job_cancellation_cancelled(job_id=job.id)
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_job_cancel__job_correctly_set_as_cancelling(self) -> None:
        await self._auth()

        job = await self._create_fake_job(self.job_executor, self.main_workspace, JobStatus.WORKING)

        output = await self._tb(["job", "cancel", job.id])

        job = Job.get_by_id(job.id)
        job.notify_cancelled_event()
        await wait_until_job_is_in_expected_status_async(job.id, [JobStatus.CANCELLED])

        expected = [
            FeedbackManager.success_job_cancellation_cancelling(job_id=job.id)
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_job_cancel__job_not_found(self) -> None:
        await self._auth()
        job_id = "job_id_not_created"

        output = await self._tb(["job", "cancel", job_id])

        expected = [
            FeedbackManager.error_job_does_not_exist(job_id=job_id)
        ]
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_job_cancel__not_permissions_to_cancel_that_job(self) -> None:
        await self._auth()

        job = await self._create_fake_job(self.job_executor, self.secondary_workspace)

        output = await self._tb(["job", "cancel", job.id])

        expected = [
            FeedbackManager.error_exception(error="Forbidden: The token you have provided doesn't have access to this resource")
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_job_cancel__job_not_in_cancellable_status(self) -> None:
        await self._auth()
        job = await self._create_fake_job(self.job_executor, self.main_workspace, JobStatus.DONE)

        output = await self._tb(["job", "cancel", job.id])

        expected = [
            FeedbackManager.error_exception(error="Job is not in cancellable status")
        ]
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_job_cancel__job_already_being_cancelled(self) -> None:
        await self._auth()
        job = await self._create_fake_job(self.job_executor, self.main_workspace, JobStatus.CANCELLING)

        output = await self._tb(["job", "cancel", job.id])

        job = Job.get_by_id(job.id)
        job.notify_cancelled_event()
        await wait_until_job_is_in_expected_status_async(job.id, [JobStatus.CANCELLED])

        expected = [
            FeedbackManager.error_exception(error="Job is already being cancelled")
        ]
        self._assert_feedback_output(expected, output)

    @staticmethod
    async def _create_fake_job(
        job_executor: JobExecutor,
        user_creating_the_job: User,
        return_it_with_state=JobStatus.WAITING
    ) -> FakeTestJob:
        if return_it_with_state in (JobStatus.CANCELLING, JobStatus.WORKING):
            cancellable_status = {JobStatus.WAITING, JobStatus.WORKING}
        else:
            cancellable_status = {JobStatus.WAITING}
        j = FakeTestJob(user_creating_the_job, cancellable_status=cancellable_status)
        j.save()
        if return_it_with_state == JobStatus.WAITING:
            return j

        job_executor.put_job(j)
        await wait_until_job_is_in_expected_status_async(j.id, [JobStatus.WORKING])
        if return_it_with_state == JobStatus.WORKING:
            return j

        if return_it_with_state == JobStatus.DONE:
            j.finish({'task': 'ok'})
            await get_finalised_job_async(j.id)
            return j

        if return_it_with_state == JobStatus.CANCELLING:
            j.try_to_cancel()
            await wait_until_job_is_in_expected_status_async(j.id, [JobStatus.CANCELLING])
            return j


async def _get_gcp_service_account_details_mock(*args, **kwargs) -> Dict[str, Any]:
    return {'account': 'fake-bigquery-account@example.com'}


async def _check_gcp_read_permissions_mock(*args, **kwargs) -> bool:
    return False


async def _list_gcp_resources_mock(*args, **kwargs) -> List[Dict[str, Any]]:
    return ["resource1", "resource2"]


# Homemade fixture because the Unittest.testcase doesn't like the pytest ones
@pytest.fixture
def mock_bq_cdk_conn():
    mock_conn = unittest.mock.create_autospec(CDKConnector)
    with patch(
        "tinybird.views.api_data_linkers.get_connector", new_callable=AsyncMock
    ) as mock_get_conn:
        with patch(
            "tinybird.views.api_data_connections.get_connector", new_callable=AsyncMock
        ) as mock_get_conn2:
            mock_get_conn.return_value = mock_conn
            mock_get_conn2.return_value = mock_conn
            yield


@pytest.fixture
def use_bq_fake_account_info():
    mock_path = "tinybird.views.api_data_connections._get_service_account_info"
    account_info = json.dumps({
        "type": "service_account",
        "project_id": "testing-project",
        "private_key_id": "8c97b0bc0184077c90736926dadc66d5f950b4ac",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCUek18Gqq2a2RO\ncQJFIZVM5Ee3YPBdN/l3hqpZPHOuZmpraKCiB5ZDwc/zL+3ght+O1poOQqJ9tJDj\nPbUz2ntdJ/lFf0qnsDUUlhuRfdNpPh7Lxw4YpBh9rz0WGKYKWWxA6z9JLuzoaE2x\nlEecMy3vmnPXWLoDygRh2qk0h3GX+uvVNnGYJ7foC2EyI+NjeRzri+cT7UJrbKha\nCnT4bJH7YfEprjM7ABnjWG4vHbjD/ag+cqtoD8JSh9BuaAzF3szmfaWSwtPAZg9b\noTus5fg5jIku/1uJJvPecmCj4VhSiJ+fTd7XA87H9wsFZjeF+etEzsGb0wTgL5Sq\nbXPSJaVhAgMBAAECggEACG9GNZWiOwiwwxACbADzZVHWjSFRpkoGvvaEeNtJSxAA\nXaes8Gdz7td0w8DmR4oB6zBfwg2hA3kdfftEbvSra2hY7czEZfBJo6i/Wi2GtATW\nZQci0t2HkqRA2R9/VzkrQCjdCIBE7xL1zu+4fbQemOzyRbqBnrN8Oj7cu+Ix3stJ\nL6NP5wM2y4thfoTDWfPHsbE2f/Orm5E0t6nu8tgLeYOxacr5OB0GZic2z19Ml4sZ\njPjb6WWyJMSnUhKM+2PKrVdX+OWJh1BrxSNtWQznt3JxZSx/1BRnca7k6O3OIf0u\niSi7dRJZirCQK+96trAWYxOE8tyGHu7STVZ5r9vobQKBgQDIX2XJLE1w+rscS6E5\ns/fjx/JNKc46UVOHn0JO6/qYMAXvNIjqzykMklkRWOohMGemDgTp+Z07sXNDXCrG\nrY2d6DmThEXPVRZCQUGNkX7UFQ0csruQgnut5IRzRyB9bgC9YGlqa+wteJG5fybZ\n5lADCmQtaSlcj6ngqbVxtuGlXwKBgQC9srQnQ7ASENntcUEBGfBd00rssT5ZOXdh\ncYF8+pFPKHOHdaJ/SYLaNtNtKWVPLmPOVn6cNrVk1dWgwYWbgEzqbbouged//oi6\n6VVDflVqqvwZhC3+1SUDrxfmXFxAmwC7GMergo2m4ItsCDsyBGnQ6B1tLw37aoSn\n0i6wdpvtPwKBgQCsPdUxaXPoep/9YsXk5F9i3q3axuUQHHjBTJWjYha4XA+94FsR\n/aI7vFH0J4qbnRB8HfD7cCdI+PEsJj5fKzFhXA6iUEHySCIqMg43s6pihPYQhVPW\nlVPb12RD9BBpwfXA1O/JG5yaOdqKqlKrXN/KvVP/9TYo6xYMmdXvOlYd4QKBgDsx\nYinGY1Cf1YDUEDapw2ljn0OQYyYwWmIbqw42mdUbiEFCobwaUiyJYxvzCNvWW+ps\n7wELyTp3xztsZ6aIOHgGWUxd2MEFyeCZIrP23ex1AklsB3Y3SF+H6WtGcrruIyI+\nrz+Dc3QZKShCwUXwPpyjcVs6jaBgMpiza0JBIJK9AoGAApo9APmcY5Fdy7YTgiY3\nYOTkXbUP5YvJU6CxuNoH6qWrdeqvkn1KMAmAOpDqs4m7EPdbjBbJPK3YBwfx+Yya\nA4CsZabsQd6kxFNpDfifDPrNPNzVYn93lAnskP/G1uP7/p9Z7MqxDw8oPXo/L35n\nyhc1F+4SZLYIclnVb4ooYFs=\n-----END PRIVATE KEY-----\n",
        "client_email": "non-existing-account@development-353413.iam.gserviceaccount.com",
        "client_id": "103929119928559871003",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/RJKgWVDuMie8R0e66VuYxVanZRh85S%40development-353413.iam.gserviceaccount.com",
    })
    with patch(mock_path, return_value=account_info):
        yield


@pytest.fixture
def mock_sf_cdk_conn():
    ROLES = [Role('role_1', '')]
    INTEGRATIONS = [Integration('tinybird_integration_role_1', '')]

    mock_conn: CDKConnector = unittest.mock.create_autospec(CDKConnector)
    mock_conn.get_roles.return_value = ROLES
    mock_conn.get_integrations.return_value = INTEGRATIONS

    with patch('tinybird.views.api_data_connectors.get_connector') as mock_get_conn:
        mock_get_conn.return_value = mock_conn
        yield


@pytest.fixture
def mock_get_or_create():
    with patch('tinybird.views.api_data_connectors.get_or_create_workspace_service_account', return_value=None):
        yield


@pytest.fixture
def use_fake_account_info():
    mock_path = "tinybird.ingest.external_datasources.admin._provision_workspace_service_account"
    fake_account_info = {
        "service_account_id": "test@project.gserviceaccount.com",
        "key": "key"
    }
    with patch(mock_path, return_value=fake_account_info):
        yield


@pytest.mark.usefixtures('mock_bq_cdk_conn')
@pytest.mark.usefixtures('use_bq_fake_account_info')
@pytest.mark.usefixtures('mock_get_or_create')
@pytest.mark.usefixtures('use_fake_account_info')
@pytest.mark.xfail(reason="Flaky ATM")
class TestCLIBigQuery(TestCLI):
    async def _create_connection(
        self,
        extra_params: Optional[List[str]] = None
    ) -> str:
        await self._auth()

        params = ["connection", "create", "bigquery"]
        if extra_params:
            params.extend(extra_params)

        return await self._tb(params, input="y\n")

    @tornado.testing.gen_test
    @patch("tinybird.ingest.external_datasources.admin.create_composer_pool")
    @patch("tinybird.ingest.external_datasources.admin.get_iam_client")
    @patch("tinybird.views.api_data_connections.list_resources")
    async def test_create_bigquery_connection(
        self,
        mock_list_resources,
        mock_iam_client,
        mock_create_composer_pool
    ) -> None:
        account_name = generate_account_name(self.workspace.id)
        mock_list_resources.return_value = ['testA', 'testB']
        mock_iam_client().get_or_create_service_account.return_value = f"{account_name}@project.com"
        mock_iam_client().generate_account_key.return_value = "fake-key"

        await self._auth()

        output = await self._create_connection()
        expected = ["created successfully"]
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    @patch("tinybird.ingest.external_datasources.admin.create_composer_pool")
    @patch("tinybird.ingest.external_datasources.admin.get_iam_client")
    @patch("tinybird.views.api_data_connections.list_resources")
    async def test_push_bigquery_datasource(
        self,
        mock_list_resources,
        mock_iam_client,
        mock_create_composer_pool
    ) -> None:
        await self._auth()

        account_name = generate_account_name(self.workspace.id)
        mock_list_resources.return_value = ['testA', 'testB']
        mock_iam_client().get_or_create_service_account.return_value = f"{account_name}@project.com"
        mock_iam_client().generate_account_key.return_value = "fake-key"

        _ = await self._create_connection()
        with tempfile.NamedTemporaryFile(suffix=".datasource", mode='w+', encoding='utf-8') as datasource_file:
            datasource_file.write("""
VERSION 0

SCHEMA >
    `O_ORDERKEY` Nullable(Int64),
    `O_CUSTKEY` Nullable(Int64)

ENGINE "MergeTree"
ENGINE_PARTITION_KEY "toYear(insertion_date)"
ENGINE_SORTING_KEY "insertion_date"

IMPORT_SERVICE 'bigquery'
IMPORT_STRATEGY 'replace'
IMPORT_QUERY 'SELECT O_ORDERKEY, O_CUSTKEY FROM TINYBIRD.SAMPLES.ORDERS_1M'
IMPORT_SCHEDULE '@once'
            """)
            datasource_file.seek(0)
            datasource_name = os.path.basename(datasource_file.name).rsplit('.', 1)[0]

            with patch("tinybird.ingest.external_datasources.connector.CDKConnector.create_stage", return_value={'stage': 'sf_stage', 'gcp_account': 'gcp_account'}):
                with patch("tinybird.views.api_data_linkers.grant_bucket_write_permissions_to_account", return_value=None):
                    with patch("tinybird.ingest.cdk_utils.CDKUtils.upload_dag", return_value=None):
                        output = await self._tb(["push", datasource_file.name])

                        expected = [
                            FeedbackManager.info_processing_file(filename=datasource_file.name),
                            FeedbackManager.info_building_dependencies(),
                            FeedbackManager.info_processing_new_resource(name=datasource_name, version='(v0)'),
                            FeedbackManager.success_create(name=f"{datasource_name}__v0")
                        ]
                        self._assert_feedback_output(expected, output)


@pytest.mark.usefixtures('mock_sf_cdk_conn')
@pytest.mark.usefixtures('mock_get_or_create')
@pytest.mark.usefixtures('use_fake_account_info')
class TestCLISnowflake(TestCLI):
    async def _create_snowflake_connection(
        self,
        conn_params: Optional[Dict[str, Any]] = None,
        extra_tb_params: Optional[List[str]] = None
    ):
        params: List[str] = ['connection', 'create', 'snowflake']

        default_conn_params: Dict[str, Any] = {
            'account': 'a',
            'username': 'b',
            'password': 'c',
            'connection-name': 'd',
            'warehouse': 'e',
            'role': 'role_1'
        }

        if conn_params:
            default_conn_params.update(conn_params)

        for k, v in default_conn_params.items():
            params.append(f'--{k}')
            params.append(v)

        if extra_tb_params:
            params += extra_tb_params

        return await self._tb(params)

    @tornado.testing.gen_test
    async def test_create_snowflake_connection(self):
        await self._auth()

        output = await self._create_snowflake_connection()

        expected = ["Validating connection...", "created successfully", "Connection details saved"]
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_create_connection_no_validate(self):
        await self._auth()

        output = await self._create_snowflake_connection(extra_tb_params=['--no-validate'])
        expected = ["created successfully"]
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_push_snowflake_datasource(self):
        await self._auth()

        _ = await self._create_snowflake_connection()

        with tempfile.NamedTemporaryFile(suffix=".datasource", mode='w+', encoding='utf-8') as datasource_file:
            datasource_file.write("""
VERSION 0

SCHEMA >
    `O_ORDERKEY` Nullable(Int64),
    `O_CUSTKEY` Nullable(Int64)

ENGINE "MergeTree"
ENGINE_PARTITION_KEY "toYear(insertion_date)"
ENGINE_SORTING_KEY "insertion_date"

IMPORT_SERVICE 'snowflake'
IMPORT_CONNECTION_NAME 'd'
IMPORT_EXTERNAL_DATA_SOURCE 'TINYBIRD.SAMPLES.ORDERS_1M'
IMPORT_STRATEGY 'replace'
IMPORT_QUERY 'SELECT O_ORDERKEY, O_CUSTKEY FROM TINYBIRD.SAMPLES.ORDERS_1M'
IMPORT_SCHEDULE '@once'
            """)
            datasource_file.seek(0)
            datasource_name = os.path.basename(datasource_file.name).rsplit('.', 1)[0]

            output: str

            with patch("tinybird.ingest.external_datasources.connector.CDKConnector.create_stage", return_value={'stage': 'sf_stage', 'gcp_account': 'gcp_account'}):
                with patch("tinybird.views.api_data_linkers.grant_bucket_write_permissions_to_account", return_value=None):
                    with patch("tinybird.ingest.cdk_utils.CDKUtils.upload_dag", return_value=None):
                        output = await self._tb(["push", datasource_file.name])

            expected = [
                FeedbackManager.info_processing_file(filename=datasource_file.name),
                FeedbackManager.info_building_dependencies(),
                FeedbackManager.info_processing_new_resource(name=datasource_name, version='(v0)'),
                FeedbackManager.success_create(name=f"{datasource_name}__v0")
            ]
            self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_pull_snowflake_datasource(self):
        await self._auth()

        _ = await self._create_snowflake_connection()

        with tempfile.NamedTemporaryFile(suffix=".datasource", mode='w+', encoding='utf-8') as datasource_file:
            datasource_file.write("""
VERSION 0

SCHEMA >
    `O_ORDERKEY` Nullable(Int64),
    `O_CUSTKEY` Nullable(Int64)

ENGINE "MergeTree"
ENGINE_PARTITION_KEY "toYear(insertion_date)"
ENGINE_SORTING_KEY "insertion_date"

IMPORT_SERVICE 'snowflake'
IMPORT_CONNECTION_NAME 'd'
IMPORT_EXTERNAL_DATA_SOURCE 'TINYBIRD.SAMPLES.ORDERS_1M'
IMPORT_STRATEGY 'replace'
IMPORT_QUERY 'SELECT O_ORDERKEY, O_CUSTKEY FROM TINYBIRD.SAMPLES.ORDERS_1M'
IMPORT_SCHEDULE 0 0 1 1 *
            """)
            datasource_file.seek(0)
            datasource_name = os.path.basename(datasource_file.name).rsplit('.', 1)[0]

            with patch("tinybird.ingest.external_datasources.connector.CDKConnector.create_stage", return_value={'stage': 'sf_stage', 'gcp_account': 'gcp_account'}):
                with patch("tinybird.views.api_data_linkers.grant_bucket_write_permissions_to_account", return_value=None):
                    with patch("tinybird.ingest.cdk_utils.CDKUtils.upload_dag", return_value=None):
                        _ = await self._tb(["push", datasource_file.name])
                        _ = await self._tb(["pull", '--match', datasource_name,
                                            '--folder', self.CLI_PROJECT_PATH])

        needed_lines = {
            "IMPORT_SERVICE 'snowflake'": False,
            "IMPORT_CONNECTION_NAME 'd'": False,
            "IMPORT_EXTERNAL_DATA_SOURCE 'TINYBIRD.SAMPLES.ORDERS_1M'": False,
            "IMPORT_STRATEGY 'replace'": False,
            "IMPORT_QUERY 'SELECT O_ORDERKEY, O_CUSTKEY FROM TINYBIRD.SAMPLES.ORDERS_1M'": False,
            "IMPORT_SCHEDULE '0 0 1 1 *'": False
        }

        with open(f'{self.CLI_PROJECT_PATH}/{datasource_name}.datasource', 'r') as pulled:
            # Walk over the pulled file and check that all the needed lines
            # are there
            for line in pulled:
                line = line.strip()
                if line in needed_lines:
                    needed_lines[line] = True

        # Assert that all the needed lines are there
        for line, exists in needed_lines.items():
            assert exists, f"Line {line} not found in pulled file"

    @tornado.testing.gen_test
    async def test_pull_snowflake_datasource_no_schedule(self):
        await self._auth()

        _ = await self._create_snowflake_connection()

        with tempfile.NamedTemporaryFile(suffix=".datasource", mode='w+', encoding='utf-8') as datasource_file:
            datasource_file.write("""
VERSION 0

SCHEMA >
    `O_ORDERKEY` Nullable(Int64),
    `O_CUSTKEY` Nullable(Int64)

ENGINE "MergeTree"
ENGINE_PARTITION_KEY "toYear(insertion_date)"
ENGINE_SORTING_KEY "insertion_date"

IMPORT_SERVICE 'snowflake'
IMPORT_CONNECTION_NAME 'd'
IMPORT_EXTERNAL_DATA_SOURCE 'TINYBIRD.SAMPLES.ORDERS_1M'
IMPORT_STRATEGY 'replace'
IMPORT_QUERY 'SELECT O_ORDERKEY, O_CUSTKEY FROM TINYBIRD.SAMPLES.ORDERS_1M'
            """)
            datasource_file.seek(0)
            datasource_name = os.path.basename(datasource_file.name).rsplit('.', 1)[0]
            with patch("tinybird.ingest.external_datasources.connector.CDKConnector.create_stage", return_value={'stage': 'sf_stage', 'gcp_account': 'gcp_account'}):
                with patch("tinybird.views.api_data_linkers.grant_bucket_write_permissions_to_account", return_value=None):
                    with patch("tinybird.ingest.cdk_utils.CDKUtils.upload_dag", return_value=None):
                        _ = await self._tb(["push", datasource_file.name])
                        _ = await self._tb(["pull", '--match', datasource_name,
                                            '--folder', self.CLI_PROJECT_PATH])

        needed_lines = {
            "IMPORT_SERVICE 'snowflake'": False,
            "IMPORT_CONNECTION_NAME 'd'": False,
            "IMPORT_EXTERNAL_DATA_SOURCE 'TINYBIRD.SAMPLES.ORDERS_1M'": False,
            "IMPORT_STRATEGY 'replace'": False,
            "IMPORT_QUERY 'SELECT O_ORDERKEY, O_CUSTKEY FROM TINYBIRD.SAMPLES.ORDERS_1M'": False,
            # IMPORT_SCHEDULE is set by default
            "IMPORT_SCHEDULE '@once'": False
        }

        with open(f'{self.CLI_PROJECT_PATH}/{datasource_name}.datasource', 'r') as pulled:
            # Walk over the pulled file and check that all the needed lines
            # are there
            for line in pulled:
                line = line.strip()
                if line in needed_lines:
                    needed_lines[line] = True

        # Assert that all the needed lines are there
        for line, exists in needed_lines.items():
            assert exists, f"Line {line} not found in pulled file"

    @tornado.testing.gen_test
    async def test_pull_snowflake_datasource_no_strategy(self):
        await self._auth()

        _ = await self._create_snowflake_connection()

        with tempfile.NamedTemporaryFile(suffix=".datasource", mode='w+', encoding='utf-8') as datasource_file:
            datasource_file.write("""
VERSION 0

SCHEMA >
    `O_ORDERKEY` Nullable(Int64),
    `O_CUSTKEY` Nullable(Int64)

ENGINE "MergeTree"
ENGINE_PARTITION_KEY "toYear(insertion_date)"
ENGINE_SORTING_KEY "insertion_date"

IMPORT_SERVICE 'snowflake'
IMPORT_CONNECTION_NAME 'd'
IMPORT_EXTERNAL_DATA_SOURCE 'TINYBIRD.SAMPLES.ORDERS_1M'
IMPORT_QUERY 'SELECT O_ORDERKEY, O_CUSTKEY FROM TINYBIRD.SAMPLES.ORDERS_1M'
IMPORT_SCHEDULE '0 0 1 1 *'
            """)
            datasource_file.seek(0)
            datasource_name = os.path.basename(datasource_file.name).rsplit('.', 1)[0]

            with patch("tinybird.ingest.external_datasources.connector.CDKConnector.create_stage", return_value={'stage': 'sf_stage', 'gcp_account': 'gcp_account'}):
                with patch("tinybird.views.api_data_linkers.grant_bucket_write_permissions_to_account", return_value=None):
                    with patch("tinybird.ingest.cdk_utils.CDKUtils.upload_dag", return_value=None):
                        _ = await self._tb(["push", datasource_file.name])
                        _ = await self._tb(["pull", '--match', datasource_name,
                                            '--folder', self.CLI_PROJECT_PATH])

        needed_lines = {
            "IMPORT_SERVICE 'snowflake'": False,
            "IMPORT_CONNECTION_NAME 'd'": False,
            "IMPORT_EXTERNAL_DATA_SOURCE 'TINYBIRD.SAMPLES.ORDERS_1M'": False,
            # IMPORT_STRATEGY is set by default
            "IMPORT_STRATEGY 'replace'": False,
            "IMPORT_QUERY 'SELECT O_ORDERKEY, O_CUSTKEY FROM TINYBIRD.SAMPLES.ORDERS_1M'": False,
            "IMPORT_SCHEDULE '0 0 1 1 *'": False
        }

        with open(f'{self.CLI_PROJECT_PATH}/{datasource_name}.datasource', 'r') as pulled:
            # Walk over the pulled file and check that all the needed lines
            # are there
            for line in pulled:
                line = line.strip()
                if line in needed_lines:
                    needed_lines[line] = True

        # Assert that all the needed lines are there
        for line, exists in needed_lines.items():
            assert exists, f"Line {line} not found in pulled file"

    @tornado.testing.gen_test
    async def test_pull_snowflake_datasource_no_service(self):
        await self._auth()

        _ = await self._create_snowflake_connection()

        with tempfile.NamedTemporaryFile(suffix=".datasource", mode='w+', encoding='utf-8') as datasource_file:
            datasource_file.write("""
VERSION 0

SCHEMA >
    `O_ORDERKEY` Nullable(Int64),
    `O_CUSTKEY` Nullable(Int64)

ENGINE "MergeTree"
ENGINE_PARTITION_KEY "toYear(insertion_date)"
ENGINE_SORTING_KEY "insertion_date"

IMPORT_CONNECTION_NAME 'd'
IMPORT_EXTERNAL_DATA_SOURCE 'TINYBIRD.SAMPLES.ORDERS_1M'
IMPORT_STRATEGY 'replace'
IMPORT_QUERY 'SELECT O_ORDERKEY, O_CUSTKEY FROM TINYBIRD.SAMPLES.ORDERS_1M'
IMPORT_SCHEDULE '0 0 1 1 *'
            """)
            datasource_file.seek(0)
            datasource_name = os.path.basename(datasource_file.name).rsplit('.', 1)[0]

            with patch("tinybird.ingest.external_datasources.connector.CDKConnector.create_stage", return_value={'stage': 'sf_stage', 'gcp_account': 'gcp_account'}):
                with patch("tinybird.views.api_data_linkers.grant_bucket_write_permissions_to_account", return_value=None):
                    with patch("tinybird.ingest.cdk_utils.CDKUtils.upload_dag", return_value=None):
                        _ = await self._tb(["push", datasource_file.name])
                        _ = await self._tb(["pull", '--match', datasource_name,
                                            '--folder', self.CLI_PROJECT_PATH])

        needed_lines = {
            # IMPORT_SERVICe is set automatically
            "IMPORT_SERVICE 'snowflake'": False,
            "IMPORT_CONNECTION_NAME 'd'": False,
            "IMPORT_EXTERNAL_DATA_SOURCE 'TINYBIRD.SAMPLES.ORDERS_1M'": False,
            "IMPORT_STRATEGY 'replace'": False,
            "IMPORT_QUERY 'SELECT O_ORDERKEY, O_CUSTKEY FROM TINYBIRD.SAMPLES.ORDERS_1M'": False,
            "IMPORT_SCHEDULE '0 0 1 1 *'": False
        }

        with open(f'{self.CLI_PROJECT_PATH}/{datasource_name}.datasource', 'r') as pulled:
            # Walk over the pulled file and check that all the needed lines
            # are there
            for line in pulled:
                line = line.strip()
                if line in needed_lines:
                    needed_lines[line] = True

        # Assert that all the needed lines are there
        for line, exists in needed_lines.items():
            assert exists, f"Line {line} not found in pulled file"


class TestCLIKafka(TestCLI):
    @tornado.testing.gen_test
    async def test_connection_happy_case(self) -> None:
        await self._auth()

        output = await self._tb(["connection", "create", "kafka",
                                 "--bootstrap-servers", CH_ADDRESS,
                                 "--key", "a",
                                 "--secret", "b"])
        expected = ["created successfully"]
        self._assert_feedback_output(expected, output)

        id = (output.split("** Connection ")[1]).split(" created")[0]
        output = await self._tb(["connection", "rm", id])
        expected = [FeedbackManager.success_delete_connection(connection_id=id)]
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_connection_happy_case_registry(self) -> None:
        await self._auth()

        output = await self._tb(["connection", "create", "kafka",
                                 "--bootstrap-servers", CH_ADDRESS,
                                 "--key", "a",
                                 "--secret", "b",
                                 "--schema-registry-url", f"http://{CH_ADDRESS}"])
        expected = ["created successfully"]
        self._assert_feedback_output(expected, output)

        id = (output.split("** Connection ")[1]).split(" created")[0]
        output = await self._tb(["connection", "rm", id])
        expected = [FeedbackManager.success_delete_connection(connection_id=id)]
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_connection_create_connection_bad_bootstrap_server(self) -> None:
        await self._auth()

        output = await self._tb(["connection", "create", "kafka",
                                 "--bootstrap-servers", "wadus",
                                 "--key", "a",
                                 "--secret", "b"],
                                assert_exit_code=1)

        expected = [FeedbackManager.error_kafka_bootstrap_server_conn()]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_connection_create_connection_bad_registry_url(self) -> None:
        await self._auth()

        output = await self._tb(["connection", "create", "kafka",
                                 "--bootstrap-servers", CH_ADDRESS,
                                 "--key", "a",
                                 "--secret", "b",
                                 "--schema-registry-url", "bad"],
                                assert_exit_code=1)

        expected = [FeedbackManager.error_kafka_registry()]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_connection_datsource_connect(self) -> None:
        await self._auth()

        with patch.object(KafkaUtils, 'get_kafka_topic_group', return_value={'response': 'ok'}):
            output = await self._tb(["connection", "create", "kafka",
                                     "--bootstrap-servers", CH_ADDRESS,
                                     "--key", "a",
                                     "--secret", "b",
                                     "--connection-name", "connection_name"])
            expected = ["created successfully"]
            self._assert_feedback_output(expected, output)

            id = (output.split("** Connection ")[1]).split(" created")[0]

            output = await self._tb(["datasource", "connect", id, "new_sd",
                                     "--topic", "a",
                                     "--group", "b",
                                     "--auto-offset-reset", "latest"])
            expected = ["Kafka streaming connection configured successfully"]
            self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_connection_ls(self) -> None:
        await self._auth()

        with patch.object(KafkaUtils, 'get_kafka_topic_group', return_value={'response': 'ok'}):
            output = await self._tb(["connection", "create", "kafka",
                                     "--bootstrap-servers", f"{CH_ADDRESS}",
                                     "--key", "a",
                                     "--secret", "b",
                                     "--connection-name", "connection_name"])
            expected = ["created successfully"]
            self._assert_feedback_output(expected, output)

            id = (output.split("** Connection ")[1]).split(" created")[0]

            output = await self._tb(["connection", "ls"])
            expected = [id, "connection_name"]
            self._assert_feedback_output(expected, output)

            output = await self._tb(["datasource", "connect", id, "new_sd",
                                     "--topic", "a",
                                     "--group", "b",
                                     "--auto-offset-reset", "latest"])
            expected = ["Kafka streaming connection configured successfully"]
            self._assert_feedback_output(expected, output)

            output = await self._tb(["datasource", "ls"])
            expected = ["kafka"]
            self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_create_kafka_without_connection_in_another_workspace(self) -> None:
        await self._auth()

        datasource_name = f"ds_{uuid.uuid4().hex}"

        with patch.object(KafkaUtils, 'get_kafka_topic_group', return_value={'response': 'ok'}):
            output = await self._tb(["connection", "create", "kafka",
                                     "--bootstrap-servers", CH_ADDRESS,
                                     "--key", "a",
                                     "--secret", "b",
                                     "--connection-name", "connection_name"])

            id = (output.split("** Connection ")[1]).split(" created")[0]

            output = await self._tb(["datasource", "connect", id, datasource_name,
                                     "--topic", "a",
                                     "--group", "b",
                                     "--auto-offset-reset", "latest"])

        output = await self._tb(["pull"])

        new_workspace = f"dev_{uuid.uuid4().hex}_new_workspace"
        await self._tb(["workspace", "create", "--user_token", self.user_token, new_workspace])
        self.workspaces_to_delete.append(Users.get_by_name(new_workspace))
        await self._tb(["workspace", "use", new_workspace])

        try:
            output = await self._tb(["push", f"{datasource_name}.datasource"])
        except Exception as e:
            expected = [f"Unknown Kafka connection in Data Source '{datasource_name}'"]
            self._assert_feedback_output(expected, str(e))


class TestOperationsWithSharedDataSources(TestCLI):

    async def _share_datasource_with_admins_workspace(self) -> None:
        tb_api_proxy_async = TBApiProxyAsync(self)

        ws_name = f"TestOperationsWithSharedDataSources_WS_{uuid.uuid4().hex}"
        email = f"{ws_name}@example.com"
        self.extra_workspace = await tb_api_proxy_async.register_user_and_workspace(email, ws_name)
        self.extra_user = UserAccount.get_by_email(email)

        token_extra_workspace = Users.get_token_for_scope(self.extra_workspace, scopes.ADMIN_USER)
        token_extra_user = UserAccounts.get_token_for_scope(self.extra_user, scopes.AUTH)

        await tb_api_proxy_async.invite_user_to_workspace(
            token=self.user_admin_token,
            workspace_id=self.workspace.id,
            user_to_invite_email=email
        )

        datasource_in_extra_workspace = await tb_api_proxy_async.create_datasource(
            token=token_extra_workspace,
            ds_name='datasource_a',
            schema='col_a Int32,col_b Int32,col_c Int32'
        )

        await tb_api_proxy_async.share_datasource_with_another_workspace(
            token=token_extra_user,
            datasource_id=datasource_in_extra_workspace['datasource']['id'],
            origin_workspace_id=self.extra_workspace.id,
            destination_workspace_id=self.workspace.id
        )

    @tornado.testing.gen_test
    async def test_pull_project_with_shared_data_sources(self) -> None:
        await self._share_datasource_with_admins_workspace()

        project_folder = Path(self.CLI_PROJECT_PATH)
        shared_ds_path = project_folder / 'vendor' / self.extra_workspace.name / 'datasource_a.datasource'

        await self._auth()
        output = await self._tb(["pull"])
        expected = [
            FeedbackManager.info_writing_resource(resource=shared_ds_path, prefix='')
        ]
        self._assert_feedback_output(expected, output)

        self.assertEqual(shared_ds_path.exists(), True, list(project_folder.iterdir()))

    @tornado.testing.gen_test
    async def test_a_pulled_shared_ds_is_ignored_on_push(self) -> None:
        await self._share_datasource_with_admins_workspace()

        await self._auth()
        await self._tb(["pull"])
        output = await self._tb(["push"])
        self.assertNotIn("datasource_a", output)

    @tornado.testing.gen_test
    # disabling this test, I don't think prefixes makes sense anymore with workspaces
    # and workspace mapping
    async def xtest_a_push_with_prefix_will_not_create_a_new_ds_for_the_shared_data_sources(self) -> None:
        await self._share_datasource_with_admins_workspace()

        await self._auth()
        await self._tb(["pull"])

        project_folder = Path(self.CLI_PROJECT_PATH)
        shared_ds_path = project_folder / 'vendor' / 'extra_workspace' / 'datasource_a.datasource'

        output = await self._tb(["push", str(shared_ds_path), '--prefix', 'newprefix'])
        self.assertNotIn('newprefix__datasource_a', output)

    @tornado.testing.gen_test
    async def test_a_push_with_prefix_will_create_a_new_pipe_for_the_shared_data_sources_and_will_correctly_replace_tables(self) -> None:
        await self._share_datasource_with_admins_workspace()

        await self._auth()
        await self._tb(["pull"])

        project_folder = Path(self.CLI_PROJECT_PATH)
        new_pipe_path = project_folder / 'extra_pipe.pipe'

        Path(new_pipe_path).write_text(f"""NODE untitled_pipe_8699_0
SQL >
    SELECT * FROM {self.extra_workspace.name}.datasource_a

        """)

        output = await self._tb(["push", str(new_pipe_path), '--push-deps', '--prefix', 'newprefix'])
        expected = [
            FeedbackManager.success_create(name='newprefix__extra_pipe')
        ]
        self._assert_feedback_output(expected, output)
        self.assertNotIn('newprefix__datasource_a', output)

        # Pipe contains the datasource also prefixed
        pipe_content = await self.http_client.fetch(
            self.get_url(f"/v0/pipes/newprefix__extra_pipe?{urlencode({'token': self.admin_token})}"), method='GET')
        self.assertEqual(pipe_content.code, 200, pipe_content.body)
        self.assertEqual(json.loads(pipe_content.body)["nodes"][0]["sql"],
                         f"SELECT * FROM {self.extra_workspace.name}.datasource_a")

    @tornado.testing.gen_test
    async def test_datasource_ls_returns_the_workspace_from_the_ds_is_shared(self) -> None:
        await self._share_datasource_with_admins_workspace()

        await self._auth()
        tb_datasource_ls_output = await self._tb(["datasource", "ls"])

        self._assert_feedback_output([
            'shared from: name: test_table',
            f'shared from: {self.extra_workspace.name}name: datasource_a',

        ], tb_datasource_ls_output)

    @tornado.testing.gen_test
    async def test_a_push_with_workspace_map(self) -> None:
        await self._share_datasource_with_admins_workspace()

        await self._auth()

        pipe_using_shared_ds = get_resource_path('test_pipe_using_shared_datasource.pipe')
        shared_wk_path = f'{os.path.dirname(__file__)}/projects/shared_workspace/'

        await self._tb(["push", str(pipe_using_shared_ds), '--workspace', 'shared_workspace', shared_wk_path, '--workspace_map', 'shared_workspace', self.extra_workspace.name])
        pipe_content = await self.http_client.fetch(
            self.get_url(f"/v0/pipes/test_pipe_using_shared_datasource?{urlencode({'token': self.admin_token})}"), method='GET')
        self.assertEqual(pipe_content.code, 200, pipe_content.body)
        # workspace should be changed to extra_workspace because of the mapping
        self.assertEqual(json.loads(pipe_content.body)["nodes"][0]["sql"], f"SELECT * FROM {self.extra_workspace.name}.datasource_a")

    @tornado.testing.gen_test
    async def test_a_push_with_workspace_should_use_local_versions(self) -> None:
        await self._share_datasource_with_admins_workspace()

        await self._auth()

        pipe_using_shared_ds = get_resource_path('test_pipe_using_shared_datasource_with_version.pipe')
        shared_wk_path = f'{os.path.dirname(__file__)}/projects/shared_workspace/'

        output = await self._tb(["push", str(pipe_using_shared_ds), '--workspace', 'shared_workspace', shared_wk_path, '--workspace_map', 'shared_workspace', self.extra_workspace.name],
                                assert_exit_code=1)
        self._assert_feedback_output([
            f"'{self.extra_workspace.name}.datasource_b__v1' not found"
        ], output)

    @tornado.testing.gen_test
    async def test_a_push_with_workspace_map_substring_naming_works_fine(self) -> None:
        await self._auth()

        pipe_using_shared_ds = get_resource_path('test_pipe_using_shared_datasource_with_version.pipe')
        shared_wk_path = f'{os.path.dirname(__file__)}/projects/shared_workspace/'

        # Create a workspace with `shared_workspace` substring at the end to check that mapping works fine
        shared_workspace = f"dev_{uuid.uuid4().hex}_shared_workspace"
        await self._tb(["workspace", "create", "--user_token", self.user_token, shared_workspace])
        self.workspaces_to_delete.append(Users.get_by_name(shared_workspace))
        await self._tb(["workspace", "use", shared_workspace])
        await self._tb(["push", shared_wk_path])

        await self._tb(["datasource", "share", "datasource_b__v1", self.workspace.name, "--user_token", self.user_token, "--yes"])
        await self._tb(["workspace", "use", self.workspace.name])

        output = await self._tb(["push", str(pipe_using_shared_ds), '--workspace_map', 'shared_workspace', shared_workspace])
        expected = [
            FeedbackManager.success_create(name='test_pipe_using_shared_datasource_with_version')
        ]
        self._assert_feedback_output(expected, output)

        pipe_content = await self.http_client.fetch(
            self.get_url(f"/v0/pipes/test_pipe_using_shared_datasource_with_version?{urlencode({'token': self.admin_token})}"), method='GET')
        self.assertEqual(pipe_content.code, 200, pipe_content.body)
        # workspace should be changed to extra_workspace because of the mapping
        self.assertEqual(json.loads(pipe_content.body)["nodes"][0]["sql"], f"SELECT * FROM {shared_workspace}.datasource_b__v1")

    @tornado.testing.gen_test
    async def test_push_with_deps_should_not_push_shared_datasources(self) -> None:
        await self._share_datasource_with_admins_workspace()

        await self._auth()

        pipe_using_shared_ds = get_resource_path('test_pipe_using_shared_datasource_with_version.pipe')
        shared_wk_path = f'{os.path.dirname(__file__)}/projects/shared_workspace/'

        output = await self._tb(["push", str(pipe_using_shared_ds), '--workspace', 'shared_workspace', shared_wk_path, '--workspace_map', 'shared_workspace', self.extra_workspace.name, '--push-deps'],
                                assert_exit_code=1)
        self._assert_feedback_output([
            f"'{self.extra_workspace.name}.datasource_b__v1' not found"
        ], output)

    @tornado.testing.gen_test
    async def test_push_a_directory(self) -> None:
        await self._share_datasource_with_admins_workspace()

        await self._auth()

        file = get_resource_path('drop-prefix/test_ds_a_good.datasource')
        path = os.path.dirname(file)

        os.chdir(path)
        output = await self._tb(['--token', self.admin_token, '--host', self.host, "push", path, "--push-deps"])

        self._assert_feedback_output([
            FeedbackManager.info_processing_file(filename=path),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.success_create(name='test_ds_a_good'),
            FeedbackManager.success_create(name='test_ds_mat'),
            FeedbackManager.success_create(name='test_pipe_populate'),
            FeedbackManager.info_materialized_datasource_used(pipe='test_pipe_populate', datasource='test_ds_mat'),
        ], output)


class TestCLIWorkspace(TestCLI):

    async def _add_extra_user_workspace(self) -> None:
        tb_api_proxy_async = TBApiProxyAsync(self)

        ws_name = f"TestCLIWorkspace_extra_workspace_{uuid.uuid4().hex}"
        email = f"{ws_name}@example.com"
        self.extra_workspace = await tb_api_proxy_async.register_user_and_workspace(email, ws_name)
        self.extra_user = UserAccount.get_by_email(email)

        extra_user_token = UserAccount.get_token_for_scope(self.extra_user, scopes.AUTH)

        await tb_api_proxy_async.invite_user_to_workspace(
            token=extra_user_token,
            workspace_id=self.extra_workspace.id,
            user_to_invite_email=self.user_account.email,
        )

    @tornado.testing.gen_test
    async def test_workspaces_are_listed_correctly(self) -> None:
        await self._auth()

        output = await self._tb(["workspace", "ls"])
        self._assert_feedback_output([
            f"name: {self.WORKSPACE}",
            f"id: {self.WORKSPACE_ID}",
            "role: admin",
            "current: True",
            "plan: Build"
        ], output)

        await self._add_extra_user_workspace()

        output = await self._tb(["workspace", "ls"])
        self._assert_feedback_output([
            f"name: {self.WORKSPACE}",
            f"id: {self.WORKSPACE_ID}",
            "role: admin",
            "current: True",
            "plan: Build",
            f"name: {self.extra_workspace.name}",
            f"id: {self.extra_workspace.id}",
            "role: guest",
            "current: False"
        ], output)

    @tornado.testing.gen_test
    async def test_workspaces_are_listed_correctly_with_workspace_admin_token(self) -> None:
        output = await self._tb(["--host", self.host, "--token", self.workspace_admin_token, "workspace", "ls"])
        self._assert_feedback_output([
            f"{self.WORKSPACE}",
            f"{self.WORKSPACE_ID}",
            "admin",
            "True",
            "Build"
        ], output)

    @tornado.testing.gen_test
    async def test_workspaces_are_listed_correctly_with_token(self) -> None:
        output = await self._tb(["--host", self.host, "--token", self.admin_token, "workspace", "ls"])
        self._assert_feedback_output([
            f"{self.WORKSPACE}",
            f"{self.WORKSPACE_ID}",
            "admin",
            "True",
            "Build"
        ], output)

        await self._add_extra_user_workspace()

        output = await self._tb(["--host", self.host, "--token", self.admin_token, "workspace", "ls"])
        self._assert_feedback_output([
            f"{self.WORKSPACE}",
            f"{self.WORKSPACE_ID}",
            "admin",
            "True",
            "Build",
            self.extra_workspace.name,
            f"{self.extra_workspace.id}",
            "guest",
            "False"
        ], output)

    @tornado.testing.gen_test
    async def test_switch_between_different_workspaces(self) -> None:
        await self._auth()
        await self._add_extra_user_workspace()

        output = await self._tb(["auth", "info"])

        self._assert_feedback_output([
            f"user: {self.user_account.email}",
            f"host: {self.host}",
            f"workspace_name: {self.WORKSPACE}",
            f"workspace_id: {self.WORKSPACE_ID}"
        ], output)

        await self._tb(["workspace", "use", self.extra_workspace.name])
        output = await self._tb(["auth", "info"])

        self._assert_feedback_output([
            f"user: {self.user_account.email}",
            f"host: {self.host}",
            f"workspace_name: {self.extra_workspace.name}",
            f"workspace_id: {self.extra_workspace.id}"
        ], output)

    @tornado.testing.gen_test
    async def test_switch_between_different_workspaces_with_token(self) -> None:
        await self._add_extra_user_workspace()

        output = await self._tb(["--host", self.host, "--token", self.admin_token, "auth", "info"])

        self._assert_feedback_output([
            f"user: {self.user_account.email}",
            f"host: {self.host}",
            f"workspace_name: {self.WORKSPACE}",
            f"workspace_id: {self.WORKSPACE_ID}"
        ], output)

        await self._tb(["--host", self.host, "--token", self.admin_token, "workspace", "use", self.extra_workspace.name])
        output = await self._tb(["--token", self.admin_token, "auth", "info"])

        self._assert_feedback_output([
            f"user: {self.user_account.email}",
            f"host: {self.host}",
            f"workspace_name: {self.extra_workspace.name}",
            f"workspace_id: {self.extra_workspace.id}"
        ], output)

    @tornado.testing.gen_test
    async def test_print_current_workspaces_with_token(self) -> None:
        await self._add_extra_user_workspace()

        output = await self._tb(["--host", self.host, "--token", self.admin_token, "workspace", "current"])

        self._assert_feedback_output([
            f"{self.WORKSPACE}",
            f"{self.WORKSPACE_ID}",
            "admin",
            "True",
            "Build",
            "True"
        ], output)

    @tornado.testing.gen_test
    async def test_create_new_workspace(self) -> None:
        await self._auth()
        workspace_to_create = f"whatever_{uuid.uuid4().hex}"

        output = await self._tb(["workspace", "create", "--user_token", self.user_token, workspace_to_create])

        self._assert_feedback_output([
            workspace_to_create,
            "created"
        ], output)

        self.workspaces_to_delete.append(Users.get_by_name(workspace_to_create))

        output = await self._tb(["workspace", "delete", "--user_token", self.user_token, workspace_to_create, "--yes"])

        self._assert_feedback_output([
            workspace_to_create,
            "deleted"
        ], output)

        with self.assertRaises(UserDoesNotExist):
            _ = Users.get_by_name(workspace_to_create)

    async def _push_object_mock(*args) -> None:
        pass

    def _get_download_url_object_mock(*args) -> str:
        return 'https://storage.googleapis.com/tinybird-tests-template/web-analytics-starter-kit.zip'

    @tornado.testing.gen_test
    async def test_create_new_workspace_interactively(self) -> None:
        await self._auth()
        workspace_to_create = f"whatever_{uuid.uuid4().hex}"

        output = await self._tb(["workspace", "create"], input=f"{self.user_token}\n1\n{workspace_to_create}\n")

        self._assert_feedback_output([
            f"** Workspace '{workspace_to_create}' has been created"
        ], output)

        self.workspaces_to_delete.append(Users.get_by_name(workspace_to_create))

        output = await self._tb(["workspace", "delete", "--user_token", self.user_token, workspace_to_create, "--yes"])

        self._assert_feedback_output([
            workspace_to_create,
            "deleted"
        ], output)

        with self.assertRaises(UserDoesNotExist):
            _ = Users.get_by_name(workspace_to_create)

    @patch.object(APIWorkspaceCreationHandler, 'push_project', _push_object_mock)
    @patch.object(APIWorkspaceCreationHandler, 'get_download_url_for_repo', _get_download_url_object_mock)
    @tornado.testing.gen_test
    async def test_create_new_workspace_interactively_with_starterkit(self) -> None:
        await self._auth()
        workspace_to_create = f"whatever_{uuid.uuid4().hex}"

        output = await self._tb(["workspace", "create"], input=f"{self.user_token}\n2\n{workspace_to_create}\n")

        self._assert_feedback_output([
            f"** Workspace '{workspace_to_create}' has been created"
        ], output)

        self.workspaces_to_delete.append(Users.get_by_name(workspace_to_create))

        output = await self._tb(["workspace", "delete", "--user_token", self.user_token, workspace_to_create, "--yes"])

        self._assert_feedback_output([
            workspace_to_create,
            "deleted"
        ], output)

        with self.assertRaises(UserDoesNotExist):
            _ = Users.get_by_name(workspace_to_create)

    @tornado.testing.gen_test
    async def test_create_new_workspace_interactively_cancelled(self) -> None:
        await self._auth()

        output = await self._tb(["workspace", "create"], input=f"{self.user_token}\n0\n")

        self._assert_feedback_output([
            '** Cancelled by user.'
        ], output)

    @patch.object(APIWorkspaceCreationHandler, 'push_project', _push_object_mock)
    @patch.object(APIWorkspaceCreationHandler, 'get_download_url_for_repo', _get_download_url_object_mock)
    @tornado.testing.gen_test
    async def test_create_new_workspace_with_starterkit(self) -> None:
        await self._auth()
        workspace_to_create = f"whatever_{uuid.uuid4().hex}"

        output = await self._tb(["workspace", "create", "--user_token", self.user_token, "--starter-kit", "web-analytics", workspace_to_create])

        self._assert_feedback_output([
            workspace_to_create,
            "created"
        ], output)

        self.workspaces_to_delete.append(Users.get_by_name(workspace_to_create))

        output = await self._tb(["workspace", "delete", "--user_token", self.user_token, workspace_to_create, "--yes"])

        self._assert_feedback_output([
            workspace_to_create,
            "deleted"
        ], output)

        with self.assertRaises(UserDoesNotExist):
            _ = Users.get_by_name(workspace_to_create)

    @tornado.testing.gen_test
    async def test_create_new_workspace_with_invalid_starterkit(self) -> None:
        await self._auth()
        workspace_to_create = f"whatever_{uuid.uuid4().hex}"

        output = await self._tb(["workspace", "create", "--user_token", self.user_token, "--starter-kit", "FAKE-starter-kit", workspace_to_create])

        self._assert_feedback_output([
            "Unknown starter kit"
        ], output)

        with self.assertRaises(UserDoesNotExist):
            _ = Users.get_by_name(workspace_to_create)

    @tornado.testing.gen_test
    async def test_create_new_workspace_with_fork(self) -> None:
        await self._auth()

        workspace_to_create = f"whatever_{uuid.uuid4().hex}"

        with tempfile.NamedTemporaryFile(suffix=".datasource", mode='w+', encoding='utf-8') as datasource_file:
            datasource_file.write("""
VERSION 0

SCHEMA >
    `id` UInt32,
    `views` UInt64

ENGINE "MergeTree"
            """)
            datasource_file.seek(0)
            datasource_name = os.path.basename(datasource_file.name).rsplit('.', 1)[0]
            output = await self._tb(["push", datasource_file.name])

            expected = [
                FeedbackManager.info_processing_file(filename=datasource_file.name),
                FeedbackManager.info_building_dependencies(),
                FeedbackManager.info_processing_new_resource(name=datasource_name, version='(v0)'),
                FeedbackManager.success_create(name=f"{datasource_name}__v0")
            ]
            self._assert_feedback_output(expected, output)

            output = await self._tb(["workspace", "create", "--user_token", self.user_token, "--fork", workspace_to_create])

            self._assert_feedback_output([
                workspace_to_create,
                "created"
            ], output)

            self.workspaces_to_delete.append(Users.get_by_name(workspace_to_create))

            output = await self._tb(["workspace", "use", workspace_to_create])
            self._assert_feedback_output([f"Now using {workspace_to_create}"], output)

            output = await self._tb(["datasource", "ls"])
            self._assert_feedback_output([datasource_name], output)

            output = await self._tb(["workspace", "delete", "--user_token", self.user_token, workspace_to_create, "--yes"])

            self._assert_feedback_output([
                workspace_to_create,
                "deleted"
            ], output)

            with self.assertRaises(UserDoesNotExist):
                _ = Users.get_by_name(workspace_to_create)

    @tornado.testing.gen_test
    async def test_delete_workspace(self) -> None:
        await self._auth()

        output = await self._tb(["workspace", "delete", "--user_token", self.user_token, "--yes", self.WORKSPACE_ID])

        self._assert_feedback_output([
            self.workspace.name,
            "deleted"
        ], output)

        with self.assertRaises(UserDoesNotExist):
            _ = Users.get_by_name(self.workspace.name)

    @tornado.testing.gen_test
    async def test_hard_delete_workspace(self) -> None:
        await self._auth()

        workspace_to_create = f"whatever_{uuid.uuid4().hex}"

        output = await self._tb(["workspace", "create", "--user_token", self.user_token, workspace_to_create])

        self._assert_feedback_output([
            workspace_to_create,
            "created"
        ], output)

        workspace_created = Users.get_by_name(workspace_to_create)
        database_created = workspace_created.database

        params = {
            'query': f"SELECT * FROM system.databases WHERE name = '{database_created}' FORMAT JSON"
        }
        r = requests.post(f'http://{CH_ADDRESS}/', params=params)
        assert r.status_code == 200, r.json()
        assert len(r.json()['data']) > 0, r.json()

        output = await self._tb(["workspace", "delete", "--user_token", self.user_token, "--yes", workspace_to_create, "--confirm_hard_delete", workspace_to_create])

        self._assert_feedback_output([
            workspace_to_create,
            "deleted"
        ], output)

        params = {
            'query': f"SELECT * FROM system.databases WHERE name = '{database_created}' FORMAT JSON"
        }
        r = requests.post(f'http://{CH_ADDRESS}/', params=params)
        assert r.status_code == 200, r.json()
        assert r.json()['data'] == [], r.json()

        with self.assertRaises(UserDoesNotExist):
            _ = Users.get_by_name(workspace_to_create)

    @tornado.testing.gen_test
    async def test_member_management(self) -> None:
        await self._auth()

        user1 = f'user1{uuid.uuid4().hex}@example.com'
        user2 = f'user2{uuid.uuid4().hex}@example.com'
        user_ne = f'non-existent{uuid.uuid4().hex}@example.com'

        # Add user1 and user2
        output = await self._tb(["workspace", "members", "add", f"{user1},{user2}", "--user_token", self.user_token])
        self.assertIn("added to workspace", output)

        # Try to add user1 again
        output = await self._tb(["workspace", "members", "add", user1, "--user_token", self.user_token])
        self.assertNotIn("added to workspace", output)

        # Remove user1
        output = await self._tb(["workspace", "members", "rm", f"{user1},{user_ne}", "--user_token", self.user_token])
        self.assertIn("removed from workspace", output)
        self.assertIn(f"The user {user_ne} does not exist", output)

        # Try to remove user1 again
        output = await self._tb(["workspace", "members", "rm", user1, "--user_token", self.user_token])
        self.assertIn(f"The user '{user1}' doesn't exist in", output)

        # List users
        output = await self._tb(["workspace", "members", "ls"])
        self.assertNotIn(user1, output)
        self.assertIn(user2, output)

        # Try to remove a non existent user
        output = await self._tb(["workspace", "members", "rm", user_ne, "--user_token", self.user_token])
        self.assertTrue("doesn't exist" in output)

    @tornado.testing.gen_test
    async def test_member_role_management(self) -> None:
        await self._auth()

        user1 = f'user1{uuid.uuid4().hex}@example.com'
        user2 = f'user2{uuid.uuid4().hex}@example.com'
        user3 = f'user3{uuid.uuid4().hex}@example.com'
        non_user = f'non_user{uuid.uuid4().hex}@example.com'

        # Try to set roles to non-existent users
        output = await self._tb(["workspace", "members", "set-role", 'admin', f'{user1},{user2}', "--user_token", self.user_token])
        self.assertIn("These users don't exist", output)

        # Add users
        await self._tb(["workspace", "members", "add", f"{user1}", "--user_token", self.user_token])
        output = await self._tb(["workspace", "members", "set-role", 'admin', f'{user1},{user2},{user3}', "--user_token", self.user_token])
        self.assertIn(f"{user1}'s role setted to admin", output)
        self.assertIn("The following users do not exist in the workspace", output)

        # Add more users
        await self._tb(["workspace", "members", "add", f"{user2},{user3}", "--user_token", self.user_token])

        # Invalid call to set-role
        output = await self._tb(["workspace", "members", "set-role", 'invalid-role', f'{user1},{user2},{user3}', "--user_token", self.user_token],
                                assert_exit_code=2)
        self.assertIn("Invalid value for", output)

        # Set role to admin
        output = await self._tb(["workspace", "members", "set-role", 'admin', f'{user1},{user2},{user3}', "--user_token", self.user_token])
        self.assertIn("Users' role setted to admin", output)

        # Set role to guest for {user1} and display a warning for {non_user}
        output = await self._tb(["workspace", "members", "set-role", 'guest', f'{user1},{non_user}', "--user_token", self.user_token])
        self.assertIn(f"{user1}'s role setted to guest", output)
        self.assertIn(f"The user {non_user} does not exist in the workspace", output)


class TestCLIBranch(TestCLI):
    @tornado.testing.gen_test
    async def test_branches_are_listed_correctly(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create"], input=f"{workspace_branch_to_create}\n")

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))
        await self._tb(["workspace", "use", self.workspace.name])
        output = await self._tb(["env", "ls"])

        # Also current workspace is print
        self._assert_feedback_output([
            self.workspace.name,
        ], output)

        self._assert_feedback_output([
            workspace_branch_to_create,
        ], output)

    @tornado.testing.gen_test
    async def test_branches_are_listed_correctly_from_branch(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create"], input=f"{workspace_branch_to_create}\n")

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))
        output = await self._tb(["env", "ls"])

        self._assert_feedback_output([
            'production',
            workspace_branch_to_create
        ], output)

    @tornado.testing.gen_test
    async def test_branches_are_listed_correctly_if_branch_name_is_used_in_multiple_workspaces(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create"], input=f"{workspace_branch_to_create}\n")

        workspace_branch = Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}")
        self.workspaces_to_delete.append(workspace_branch)

        # create new workspace
        workspace_to_create = f"new_workspace_{uuid.uuid4().hex}"
        output = await self._tb(["workspace", "create", "--user_token", self.user_token, workspace_to_create])

        self._assert_feedback_output([
            workspace_to_create,
            "created"
        ], output)
        self.workspaces_to_delete.append(Users.get_by_name(workspace_to_create))

        new_workspace = User.get_by_name(workspace_to_create)
        with User.transaction(new_workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True

        await self._tb(["workspace", "use", workspace_to_create])

        output = await self._tb(["env", "create"], input=f"{workspace_branch_to_create}\n")

        new_workspace_branch = Users.get_by_name(f"{workspace_to_create}_{workspace_branch_to_create}")
        self.workspaces_to_delete.append(new_workspace_branch)

        output = await self._tb(["env", "ls"])

        self._assert_feedback_output([
            self.workspace.name,
            workspace_branch.id
        ], output, not_in=True)

        self._assert_feedback_output([
            workspace_branch_to_create,
            new_workspace_branch.id
        ], output)

    @tornado.testing.gen_test
    async def test_create_branch(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create", workspace_branch_to_create])

        self._assert_feedback_output([
            f"** Environment '{workspace_branch_to_create}' from '{self.workspace.name}' has been created"
        ], output)

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        output = await self._tb(["env", "use", workspace_branch_to_create])
        self._assert_feedback_output([f"Now using {workspace_branch_to_create}"], output)

        output = await self._tb(["env", "data", "--all", "--wait"])
        self._assert_feedback_output(["Partitions from production Workspace have been attached to the Environment"], output)

        output = await self._tb(["sql", "select count() from test_table"])
        self._assert_feedback_output(["-----------| count() |-----------|       6 |-----------"], output)

        output = await self._tb(["env", "ls"])
        self._assert_feedback_output([workspace_branch_to_create], output.split('Environments')[1])

        output = await self._tb(["workspace", "use", self.workspace.name])
        output = await self._tb(["env", "ls"])
        self._assert_feedback_output([workspace_branch_to_create, self.workspace.name], output)

        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = False

    @tornado.testing.gen_test
    async def test_create_branch_disabled_branching(self) -> None:
        await self._auth()
        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create", workspace_branch_to_create], assert_exit_code=1)

        self._assert_feedback_output([
            "** This command depends on the experimental Environments feature currently in beta."
        ], output)

    @tornado.testing.gen_test
    async def test_create_branch_nok_from_other_branch(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create", workspace_branch_to_create])

        self._assert_feedback_output([
            f"** Environment '{workspace_branch_to_create}' from '{self.workspace.name}' has been created"
        ], output)

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        output = await self._tb(["env", "use", workspace_branch_to_create])
        self._assert_feedback_output([f"Now using {workspace_branch_to_create}"], output)

        workspace_another_branch_to_create = f"another_branch_{uuid.uuid4().hex}"
        output = await self._tb(["env", "create", workspace_another_branch_to_create], assert_exit_code=1)

        self._assert_feedback_output([
            f"** Environment can't be created from other Environment '{workspace_branch_to_create}'"
        ], output)

    @tornado.testing.gen_test
    async def test_create_branch_nok_unique_name(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create", workspace_branch_to_create])

        self._assert_feedback_output([
            f"** Environment '{workspace_branch_to_create}' from '{self.workspace.name}' has been created"
        ], output)

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        output = await self._tb(["workspace", "use", self.workspace.name])

        output = await self._tb(["env", "create", workspace_branch_to_create], assert_exit_code=1)

        self._assert_feedback_output([workspace_branch_to_create, 'Environment names should be unique.'], output)

    @tornado.testing.gen_test
    async def test_create_branch_same_name_different_workspace(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create", workspace_branch_to_create])

        self._assert_feedback_output([
            f"** Environment '{workspace_branch_to_create}' from '{self.workspace.name}' has been created"
        ], output)

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        workspace_to_create = f"ws_{uuid.uuid4().hex}"
        output = await self._tb(["workspace", "create", "--user_token", self.user_token, workspace_to_create])
        self._assert_feedback_output([
            workspace_to_create,
            "created"
        ], output)
        new_workspace = User.get_by_name(workspace_to_create)
        self.workspaces_to_delete.append(new_workspace)
        with User.transaction(new_workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True

        await self._tb(["workspace", "use", workspace_to_create])

        output = await self._tb(["env", "create"], input=f"{workspace_branch_to_create}\n")

        self._assert_feedback_output([
            f"** Environment '{workspace_branch_to_create}' from '{workspace_to_create}' has been created"
        ], output)

        new_workspace_branch = Users.get_by_name(f"{workspace_to_create}_{workspace_branch_to_create}")
        self.workspaces_to_delete.append(new_workspace_branch)

    @tornado.testing.gen_test
    async def test_data_branch_validations(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create", workspace_branch_to_create, '--last-partition', '--all'])
        self._assert_feedback_output(['Use --last-partition or --all but not both'], output)

        output = await self._tb(["env", "create", workspace_branch_to_create])

        self._assert_feedback_output([
            f"** Environment '{workspace_branch_to_create}' from '{self.workspace.name}' has been created"
        ], output)

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        output = await self._tb(["env", "use", workspace_branch_to_create])
        self._assert_feedback_output([f"Now using {workspace_branch_to_create}"], output)

        output = await self._tb(["env", "data"])
        self._assert_feedback_output(['Use --last-partition or --all'], output)

        output = await self._tb(["env", "data", "--last-partition", '--all'])
        self._assert_feedback_output(['Use --last-partition or --all but not both'], output)

    @tornado.testing.gen_test
    async def test_create_branch_with_attach_last_partition(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create", workspace_branch_to_create, "--last-partition"])

        self._assert_feedback_output([
            f"** Environment '{workspace_branch_to_create}' from '{self.workspace.name}' has been created",
            f"Now using {workspace_branch_to_create}",
            'Partition',
            'Done'
        ], output)

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        output = await self._tb(["sql", "select count() from test_table"])
        self._assert_feedback_output(["-----------| count() |-----------|       1 |-----------"], output)
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = False

    @tornado.testing.gen_test
    async def test_create_branch_with_attach_all_partitions(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create", workspace_branch_to_create, "--all", '--wait'])
        self._assert_feedback_output([
            f"** Environment '{workspace_branch_to_create}' from '{self.workspace.name}' has been created",
            f"Now using {workspace_branch_to_create}",
            'Data Branch job url',
            'Data Branching',
            'Done'
        ], output)

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = False

        output = await self._tb(["sql", "select count() from test_table"])
        self._assert_feedback_output(["-----------| count() |-----------|       6 |-----------"], output)
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = False

    @tornado.testing.gen_test
    async def test_create_branch_with_error(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()

        output = await self._tb(["env", "data", "--all"])
        self._assert_feedback_output(["Command disabled for 'production' Environment"], output)

        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = False

    @tornado.testing.gen_test
    async def test_create_branch_interactively(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create"], input=f"{workspace_branch_to_create}\n")

        self._assert_feedback_output([
            f"** Environment '{workspace_branch_to_create}' from '{self.workspace.name}' has been created",
            f"Now using {workspace_branch_to_create}"
        ], output)

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = False

    @tornado.testing.gen_test
    async def test_delete_branch(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create"], input=f"{workspace_branch_to_create}\n")

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        output = await self._tb(["env", "rm", "--yes", workspace_branch_to_create])
        self._assert_feedback_output([
            workspace_branch_to_create,
            "deleted",
            f"Now using {self.workspace.name}"
        ], output)

        with self.assertRaises(UserDoesNotExist):
            _ = Users.get_by_name(workspace_branch_to_create)

    @tornado.testing.gen_test
    async def test_delete_branch_nok_if_workspace(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create"], input=f"{workspace_branch_to_create}\n")

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        output = await self._tb(["env", "rm", "--yes", self.workspace.name],
                                assert_exit_code=1)

        self._assert_feedback_output([
            f"Environment {self.workspace.name} not found"
        ], output)

        u = Users.get_by_name(self.workspace.name)
        self.assertEqual(self.workspace.id, u.id)

    @tornado.testing.gen_test
    async def test_delete_branch_nok_for_main(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create"], input=f"{workspace_branch_to_create}\n")

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        output = await self._tb(["env", "rm", "--yes", "production"])

        self._assert_feedback_output([
            "Command disabled for 'production' Environment"
        ], output)

        u = Users.get_by_name(self.workspace.name)
        self.assertEqual(self.workspace.id, u.id)

    @tornado.testing.gen_test
    async def test_delete_branch_nok_if_branch_in_other_workspace(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create"], input=f"{workspace_branch_to_create}\n")

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        workspace_to_create = f"ws_{uuid.uuid4().hex}"
        output = await self._tb(["workspace", "create", "--user_token", self.user_token, workspace_to_create])
        self._assert_feedback_output([
            workspace_to_create,
            "created"
        ], output)
        new_workspace = User.get_by_name(workspace_to_create)
        self.workspaces_to_delete.append(new_workspace)

        with User.transaction(new_workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True

        output = await self._tb(["workspace", "use", workspace_to_create])

        output = await self._tb(["env", "rm", "--yes", workspace_branch_to_create],
                                assert_exit_code=1)

        self._assert_feedback_output([
            f"Environment {workspace_branch_to_create} not found"
        ], output)

    @tornado.testing.gen_test
    async def test_workspace_ls(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create"], input=f"{workspace_branch_to_create}\n")

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        output = await self._tb(["workspace", "ls"])

        self._assert_feedback_output([
            self.workspace.name,
        ], output)

        self._assert_feedback_output([
            workspace_branch_to_create,
        ], output, not_in=True)

    @tornado.testing.gen_test
    async def test_branch_use(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create"], input=f"{workspace_branch_to_create}\n")

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        output = await self._tb(["env", "use", workspace_branch_to_create])

        self._assert_feedback_output([
            "Now using",
            workspace_branch_to_create,
        ], output)

    @tornado.testing.gen_test
    async def test_branch_use_main(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create"], input=f"{workspace_branch_to_create}\n")

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        output = await self._tb(["env", "use", workspace_branch_to_create])

        output = await self._tb(["env", "use", "production"])

        self._assert_feedback_output([
            "Now using",
            self.workspace.name,
            self.workspace.id,
        ], output)

    @tornado.testing.gen_test
    async def test_branch_use_not_exists(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "use", workspace_branch_to_create])

        self._assert_feedback_output([
            f"Environment {workspace_branch_to_create} not found"
        ], output)

    @tornado.testing.gen_test
    async def test_branch_use_not_from_current_workspace(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create"], input=f"{workspace_branch_to_create}\n")
        branch = Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}")
        self.workspaces_to_delete.append(branch)
        # create new workspace
        workspace_to_create = f"new_workspace_{uuid.uuid4().hex}"
        output = await self._tb(["workspace", "create", "--user_token", self.user_token, workspace_to_create])

        self._assert_feedback_output([
            workspace_to_create,
            "created"
        ], output)
        new_workspace = Users.get_by_name(workspace_to_create)
        self.workspaces_to_delete.append(new_workspace)

        with User.transaction(new_workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True

        output = await self._tb(["workspace", "use", workspace_to_create])

        output = await self._tb(["env", "create"], input=f"{workspace_branch_to_create}\n")
        new_workspace_branch = Users.get_by_name(f"{workspace_to_create}_{workspace_branch_to_create}")
        self.workspaces_to_delete.append(new_workspace_branch)

        output = await self._tb(["env", "use", workspace_branch_to_create])
        self._assert_feedback_output([
            "Now using",
            workspace_branch_to_create,
            new_workspace_branch.id
        ], output)

        output = await self._tb(["workspace", "use", self.workspace.name])

        output = await self._tb(["env", "use", workspace_branch_to_create])
        self._assert_feedback_output([
            "Now using",
            workspace_branch_to_create,
            branch.id
        ], output)

    @tornado.testing.gen_test
    async def test_workspace_clear_over_branch(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create"], input=f"{workspace_branch_to_create}\n")

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        output = await self._tb(["env", "use", workspace_branch_to_create])

        output = await self._tb(["workspace", "clear", "--yes"])

        self._assert_feedback_output([
            "Command disabled for Environments"
        ], output)

        self._assert_feedback_output([
            "Removing"
        ], output, not_in=True)

    @tornado.testing.gen_test
    async def test_branch_diff(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        await self._tb(["env", "create", workspace_branch_to_create])
        output = await self._tb(["pull", "--auto"])

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        with open('pipes/test_pipe.pipe', "w") as pipe_file:
            pipe_file.write("""
NODE mv
SQL >

    SELECT 1""")

        output = await self._tb(["push", 'pipes/test_pipe.pipe', '--force'])

        with open('pipes/test_pipe.pipe', "w") as pipe_file:
            pipe_file.write("""
NODE mv
SQL >

    SELECT 2""")

        # diff of a single file
        output = await self._tb(["diff", 'pipes/test_pipe.pipe', "--no-color", "--production"])
        self.assertTrue("test_pipe.pipe [remote]+++ pipes/test_pipe.pipe [local]@@ -1,5 +1,5 @@-NODE test_pipe_0+NODE mv SQL >-    select * from test_table+    SELECT 2" in output)

        # diff of a single file with fmt to the branch
        output = await self._tb(["diff", 'pipes/test_pipe.pipe', "--no-color"])
        self.assertTrue("test_pipe.pipe [remote]+++ pipes/test_pipe.pipe [local]@@ -1,5 +1,5 @@ NODE mv SQL >-    SELECT 1+    SELECT 2" in output)

        # diff of a single file with fmt
        output = await self._tb(["diff", 'pipes/test_pipe.pipe', "--no-color", "--production"])
        self.assertTrue("test_pipe.pipe [remote]+++ pipes/test_pipe.pipe [local]@@ -1,5 +1,5 @@-NODE test_pipe_0+NODE mv SQL >-    select * from test_table+    SELECT 2" in output)

        # push a resource to the branch and it's not in the diff output because it checks the origin workspace
        file = self._get_resource_path('test_ds_engine_ttl.datasource')
        await self._tb(["push", file])
        output = await self._tb(["diff", "--no-color", "--production"])
        self.assertTrue('test_ds_engine_ttl only exists in remote' not in output)

        await self._tb(["workspace", "use", self.workspace.name])
        output = await self._tb(["diff", "--no-color", "--production"])
        self.assertTrue("To use this command you need to be authenticated on an Environment. Use 'tb env ls' and 'tb env use' and retry the command." in output)

    @tornado.testing.gen_test
    async def test_regression_tests_over_branch(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        name = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file])

        name = 'test_pipe_a_good'
        file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", file])

        with tempfile.NamedTemporaryFile(suffix='.csv', mode='w+', encoding='utf-8') as append_file:
            append_file.write('1,test1,test2')
            append_file.seek(0)
            await self._tb(["datasource", "append", "test_ds_a_good", append_file.name])

        output = await self._tb(["pipe", "data", name])

        self.force_flush_of_span_records()
        self.wait_for_public_table_replication('pipe_stats_rt')

        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create", "--all", "--wait"], input=f"{workspace_branch_to_create}\n")

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        output = await self._tb(["env", "use", workspace_branch_to_create])

        # run regression-tests with requests from branch
        output = await self._tb(["pipe", "regression-test", file, "--check-requests-from-production"])

        expected = [
            FeedbackManager.info_processing_file(filename=file),
            FeedbackManager.info_building_dependencies(),

        ]
        self._assert_feedback_output(expected, output)

        unexpected = [
            FeedbackManager.success_create(name=name),
            FeedbackManager.info_not_pushing_fixtures(),
            "Test Passed",
            "Response Time Metrics"
        ]
        self._assert_feedback_output(unexpected, output, not_in=True)

        # run regression-tests with requests from main is default behavior
        output = await self._tb(["pipe", "regression-test", file])

        self.force_flush_of_span_records()
        self.wait_for_public_table_replication('pipe_stats_rt')

        expected = [
            FeedbackManager.info_processing_file(filename=file),
            FeedbackManager.info_building_dependencies(),
            "Test Passed",
            "Response Time Metrics"
        ]
        self._assert_feedback_output(expected, output)

        unexpected = [
            FeedbackManager.success_create(name=name),
            FeedbackManager.info_not_pushing_fixtures(),
        ]
        self._assert_feedback_output(unexpected, output, not_in=True)

    @tornado.testing.gen_test
    async def test_branch_current_from_main(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        output = await self._tb(["env", "current"])

        self._assert_feedback_output(["production", self.workspace.id, self.workspace.name], output)

    @tornado.testing.gen_test
    async def test_branch_current_from_branch(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()

        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create"], input=f"{workspace_branch_to_create}\n")

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        await self._tb(["env", "use", workspace_branch_to_create])

        output = await self._tb(["env", "current"])

        self._assert_feedback_output([workspace_branch_to_create, self.workspace.name], output)

        self._assert_feedback_output([self.workspace.id], output, not_in=True)

    @tornado.testing.gen_test
    async def test_workspace_current_from_a_branch(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()

        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create"], input=f"{workspace_branch_to_create}\n")

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        output = await self._tb(["env", "use", workspace_branch_to_create])

        output = await self._tb(["workspace", "current"])

        self._assert_feedback_output([self.workspace.name, self.workspace.id], output)

        self._assert_feedback_output([workspace_branch_to_create], output, not_in=True)

    @tornado.testing.gen_test
    async def test_branch_copy_from_main(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()

        expected = await self._tb(["sql", f"SELECT count() as c FROM {self.datasource_name}"])

        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create"], input=f"{workspace_branch_to_create}\n")

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        output = await self._tb(["env", "use", workspace_branch_to_create])

        output = await self._tb(["env", "datasource", "copy", self.datasource_name, "--sql-from-production", "--wait"])

        output = await self._tb(["sql", f"SELECT count() as c FROM {self.datasource_name}"])

        self._assert_feedback_output(expected, self._clean_output(output))

    @tornado.testing.gen_test
    async def test_branch_copy_from_main_no_args(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()

        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create"], input=f"{workspace_branch_to_create}\n")

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        output = await self._tb(["env", "use", workspace_branch_to_create])

        output = await self._tb(["env", "datasource", "copy", self.datasource_name, "--wait"])

        expected = ["Use --sql or --sql-from-production"]

        self._assert_feedback_output(expected, self._clean_output(output))

    @tornado.testing.gen_test
    async def test_main_branch_copy_from_main(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()

        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create"], input=f"{workspace_branch_to_create}\n")

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        output = await self._tb(["env", "use", "production"])

        output = await self._tb(["env", "datasource", "copy", self.datasource_name, "--sql-from-production", "--wait"])

        expected = ["Command disabled for 'production' Environment"]

        self._assert_feedback_output(expected, self._clean_output(output))

    @tornado.testing.gen_test
    async def test_main_branch_copy_from_main_with_sql(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()

        expected = await self._tb(["sql", f"SELECT count() as c FROM {self.datasource_name}"])

        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create"], input=f"{workspace_branch_to_create}\n")

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        output = await self._tb(["env", "use", workspace_branch_to_create])

        output = await self._tb(["env", "datasource", "copy", self.datasource_name, "--sql", f"select * from production.{self.datasource_name}", "--wait"])

        output = await self._tb(["sql", f"SELECT count() as c FROM {self.datasource_name}"])

        self._assert_feedback_output(expected, self._clean_output(output))

    @tornado.testing.gen_test
    async def test_regression_tests_branch_vs_main_all_pipes_coverage(self) -> None:

        # patch api_host settings
        self.app.settings["api_host"] = self.get_host()
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        name = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file])

        name = 'test_pipe_a_good_encoding'
        file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", file])

        name = 'test_pipe_a_good'
        file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", file])

        with tempfile.NamedTemporaryFile(suffix='.csv', mode='w+', encoding='utf-8') as append_file:
            append_file.write('1,test1,test2')
            append_file.seek(0)
            await self._tb(["datasource", "append", "test_ds_a_good", append_file.name])

        output = await self._tb(["pipe", "data", name])

        self.force_flush_of_span_records()
        self.wait_for_public_table_replication('pipe_stats_rt')

        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create", "--all", "--wait"], input=f"{workspace_branch_to_create}\n")

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        output = await self._tb(["env", "use", workspace_branch_to_create])

        # run regression-tests from branch to main
        for args in [["env", "regression-tests", "coverage", "--assert-time-increase-percentage", "-1", "--wait"], ["env", "regression-tests", "--wait"]]:
            output = await self._tb(args)

            expected = [
                FeedbackManager.info_regression_tests_branch_job_url(url=''),
                'test_pipe_a_good.json',
                "Passed",
                "OK - test_pipe_a_good(coverage)",
                "Performance metrics"
            ]
            self._assert_feedback_output(expected, output)

            unexpected = [
                FeedbackManager.success_create(name=name),
                FeedbackManager.info_not_pushing_fixtures(),
                'Failures',
                'FAILED',
                'ERROR'
            ]
            self._assert_feedback_output(unexpected, output, not_in=True)

    @tornado.testing.gen_test
    async def test_regression_tests_branch_vs_main_all_pipes_last(self) -> None:

        # patch api_host settings
        self.app.settings["api_host"] = self.get_host()
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        name = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file])

        name = 'test_pipe_a_good_encoding'
        file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", file])

        name = 'test_pipe_a_good'
        file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", file])

        with tempfile.NamedTemporaryFile(suffix='.csv', mode='w+', encoding='utf-8') as append_file:
            append_file.write('1,test1,test2')
            append_file.seek(0)
            await self._tb(["datasource", "append", "test_ds_a_good", append_file.name])

        output = await self._tb(["pipe", "data", name])

        self.force_flush_of_span_records()
        self.wait_for_public_table_replication('pipe_stats_rt')

        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create", "--all", "--wait"], input=f"{workspace_branch_to_create}\n")

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        output = await self._tb(["env", "use", workspace_branch_to_create])

        # run regression-tests from branch to main
        output = await self._tb(["env", "regression-tests", "last", "--assert-time-increase-percentage", "-1", "--wait"])

        expected = [
            FeedbackManager.info_regression_tests_branch_job_url(url=''),
            'test_pipe_a_good.json',
            "OK - test_pipe_a_good(last)",
            "Passed",
            "Performance metrics"
        ]
        self._assert_feedback_output(expected, output)

        unexpected = [
            FeedbackManager.success_create(name=name),
            FeedbackManager.info_not_pushing_fixtures(),
            'Failures'
            'FAILED',
            'ERROR'
        ]
        self._assert_feedback_output(unexpected, output, not_in=True)

    @tornado.testing.gen_test
    async def test_regression_tests_branch_vs_main_pipe_argument_coverage(self) -> None:
        # patch api_host settings
        self.app.settings["api_host"] = self.get_host()
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        name = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file])

        name = 'test_pipe_a_good_encoding'
        file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", file])

        name = 'test_pipe_a_good'
        file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", file])

        with tempfile.NamedTemporaryFile(suffix='.csv', mode='w+', encoding='utf-8') as append_file:
            append_file.write('1,test1,test2')
            append_file.seek(0)
            await self._tb(["datasource", "append", "test_ds_a_good", append_file.name])

        output = await self._tb(["pipe", "data", name])

        self.force_flush_of_span_records()
        self.wait_for_public_table_replication('pipe_stats_rt')

        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create", "--all", "--wait"], input=f"{workspace_branch_to_create}\n")

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        output = await self._tb(["env", "use", workspace_branch_to_create])

        # run regression-tests from branch to main
        output = await self._tb(["env", "regression-tests", "coverage", "test_pipe_a_good", "--assert-time-increase-percentage", "-1", "--wait"])

        expected = [
            FeedbackManager.info_regression_tests_branch_job_url(url=''),
            "test_pipe_a_good.json",
            "OK - test_pipe_a_good(coverage)",
            "Passed",
            "Performance metrics"
        ]
        self._assert_feedback_output(expected, output)

        unexpected = [
            FeedbackManager.success_create(name=name),
            FeedbackManager.info_not_pushing_fixtures(),
            "test_pipe_a_good_encoding.json",
            'FAILED',
            'Failures'
            'ERROR'
        ]
        self._assert_feedback_output(unexpected, output, not_in=True)

    @tornado.testing.gen_test
    async def test_regression_tests_branch_vs_main_pipe_argument_as_regex_coverage(self) -> None:
        # patch api_host settings
        self.app.settings["api_host"] = self.get_host()
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        name = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file])

        name = 'test_pipe_a_good_encoding'
        file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", file])

        name = 'test_pipe_a_good'
        file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", file])

        with tempfile.NamedTemporaryFile(suffix='.csv', mode='w+', encoding='utf-8') as append_file:
            append_file.write('1,test1,test2')
            append_file.seek(0)
            await self._tb(["datasource", "append", "test_ds_a_good", append_file.name])

        output = await self._tb(["pipe", "data", name])

        output = await self._tb(["pipe", "data", 'test_pipe_a_good_encoding'])

        self.force_flush_of_span_records()
        self.wait_for_public_table_replication('pipe_stats_rt')

        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create", "--all", "--wait"], input=f"{workspace_branch_to_create}\n")

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        output = await self._tb(["env", "use", workspace_branch_to_create])

        # run regression-tests from branch to main
        output = await self._tb(["env", "regression-tests", "coverage", "test_pipe_a_good.*", "--assert-time-increase-percentage", "-1", "--wait"])

        expected = [
            FeedbackManager.info_regression_tests_branch_job_url(url=''),
            "test_pipe_a_good.json",
            "test_pipe_a_good_encoding.json",
            "OK - test_pipe_a_good(coverage)",
            "OK - test_pipe_a_good_encoding(coverage)",
            "Passed",
            "Performance metrics"
        ]
        self._assert_feedback_output(expected, output)

        unexpected = [
            FeedbackManager.success_create(name=name),
            FeedbackManager.info_not_pushing_fixtures(),
            'FAILED',
            'Failures'
            'ERROR'
        ]
        self._assert_feedback_output(unexpected, output, not_in=True)

    @tornado.testing.gen_test
    async def test_regression_tests_branch_vs_main_pipe_argument_manual(self) -> None:
        # patch api_host settings
        self.app.settings["api_host"] = self.get_host()
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        name = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file])

        name = 'test_pipe_a_good_encoding'
        file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", file])

        name = 'test_pipe_a_good'
        file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", file])

        with tempfile.NamedTemporaryFile(suffix='.csv', mode='w+', encoding='utf-8') as append_file:
            append_file.write('1,test1,test2')
            append_file.seek(0)
            await self._tb(["datasource", "append", "test_ds_a_good", append_file.name])

        output = await self._tb(["pipe", "data", name])

        self.force_flush_of_span_records()
        self.wait_for_public_table_replication('pipe_stats_rt')

        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create", "--all", "--wait"], input=f"{workspace_branch_to_create}\n")

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        output = await self._tb(["env", "use", workspace_branch_to_create])

        # run regression-tests from branch to main
        output = await self._tb(["env", "regression-tests", "manual", "test_pipe_a_good", "--param", "1", "--assert-time-increase-percentage", "-1", "--wait"])

        expected = [
            FeedbackManager.info_regression_tests_branch_job_url(url=''),
            "OK - test_pipe_a_good(manual)",
            "test_pipe_a_good.json?param=1&pipe_checker=true",
            "Passed",
            "Performance metrics"
        ]
        self._assert_feedback_output(expected, output)

        unexpected = [
            FeedbackManager.success_create(name=name),
            FeedbackManager.info_not_pushing_fixtures(),
            "test_pipe_a_good_encoding.json",
            'Failures'
            'FAILED',
            'ERROR'
        ]
        self._assert_feedback_output(unexpected, output, not_in=True)

    @tornado.testing.gen_test
    async def test_regression_tests_branch_vs_main_filename(self) -> None:
        # patch api_host settings
        self.app.settings["api_host"] = self.get_host()
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()
        name = 'test_ds_a_good'
        file = self._get_resource_path(f'{name}.datasource')
        output = await self._tb(["push", file])

        name = 'test_pipe_a_good_encoding'
        file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", file])

        name = 'test_pipe_a_good'
        file = self._get_resource_path(f'{name}.pipe')
        output = await self._tb(["push", file])

        with tempfile.NamedTemporaryFile(suffix='.csv', mode='w+', encoding='utf-8') as append_file:
            append_file.write('1,test1,test2')
            append_file.seek(0)
            await self._tb(["datasource", "append", "test_ds_a_good", append_file.name])

        output = await self._tb(["pipe", "data", name])

        self.force_flush_of_span_records()
        self.wait_for_public_table_replication('pipe_stats_rt')

        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create", "--all", "--wait"], input=f"{workspace_branch_to_create}\n")

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))

        output = await self._tb(["env", "use", workspace_branch_to_create])

        file_regression = self._get_resource_path('pipe_a_good_regression.yaml')

        # run regression-tests from branch to main
        output = await self._tb(["env", "regression-tests", "--filename", file_regression, "--wait"])

        expected = [
            FeedbackManager.info_regression_tests_branch_job_url(url=''),
            "OK - test_pipe_a_good(coverage)",
            "test_pipe_a_good.json?date_from=2020-01-01&date_to=2021-01-01&pipe_checker=true ",
            "Passed",
            "Performance metrics"
        ]
        self._assert_feedback_output(expected, output)

        unexpected = [
            FeedbackManager.success_create(name=name),
            FeedbackManager.info_not_pushing_fixtures(),
            "test_pipe_a_good_encoding.json",
            'Failures',
            'FAILED'
            'ERROR'
        ]
        self._assert_feedback_output(unexpected, output, not_in=True)

    @tornado.testing.gen_test
    async def test_branches_with_tuple_datasource(self) -> None:
        with User.transaction(self.workspace.id) as w:
            w.feature_flags[FeatureFlagWorkspaces.BRANCHING.value] = True
        await self._auth()

        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        datasource_file.write("""
SCHEMA >
    id UUID `json:$.id`

ENGINE "MergeTree"
ENGINE_PARTITION_KEY ""
ENGINE_SORTING_KEY tuple()
            """)

        datasource_file.seek(0)
        output = await self._tb(["push", datasource_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=datasource_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=datasource_name, version=''),
            FeedbackManager.success_create(name=datasource_name)
        ]

        self._assert_feedback_output(expected, output)

        (endpoint_file, endpoint_name) = self.create_tmp_file(suffix='.pipe')
        endpoint_file.write("""
NODE endpoint
SQL >
    SELECT id
    FROM generateRandom('id UUID')
    LIMIT 1000
            """)

        endpoint_file.seek(0)
        output = await self._tb(["push", endpoint_file.name])
        expected = [
            FeedbackManager.info_processing_file(filename=endpoint_file.name),
            FeedbackManager.info_building_dependencies(),
            FeedbackManager.info_processing_new_resource(name=endpoint_name, version=''),
            FeedbackManager.success_create(name=endpoint_name)
        ]

        self._assert_feedback_output(expected, output)

        output = await self._tb(["datasource", "append", datasource_name, f"{self.host}/v0/pipes/{endpoint_name}.ndjson?token={self.admin_token}"])
        expected = [
            FeedbackManager.info_starting_import_process(),
            FeedbackManager.success_progress_blocks(),
            FeedbackManager.success_total_rows(datasource=datasource_name, total_rows=1000),
            FeedbackManager.success_appended_datasource(datasource=datasource_name),
            FeedbackManager.info_data_pushed(datasource=datasource_name)
        ]
        self._assert_feedback_output(expected, output)

        workspace_branch_to_create = f"branch_{uuid.uuid4().hex}"

        output = await self._tb(["env", "create", "--last-partition"], input=f"{workspace_branch_to_create}\n")

        self.workspaces_to_delete.append(Users.get_by_name(f"{self.workspace.name}_{workspace_branch_to_create}"))
        output = await self._tb(["env", "ls"])

        self._assert_feedback_output([
            'production',
            workspace_branch_to_create
        ], output)

        output = await self._tb(["env", "use", workspace_branch_to_create])
        self._assert_feedback_output([f"Now using {workspace_branch_to_create}"], output)

        output = await self._tb(["sql", f"SELECT count() FROM {datasource_name}", "--format", "csv"])
        expected = ['1000']
        self._assert_feedback_output(expected, output)


class TestCLIVersion(TestCLI):
    @tornado.testing.gen_test
    async def test_sql__version_message_shown_by_default(self) -> None:
        await self._auth()

        output = await self._tb(["sql", "SELECT 1"], env={'PYTEST': ""})

        expected = [FeedbackManager.warning_development_cli()]
        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_sql__version_message_not_shown_when_parameter_is_added(self) -> None:
        await self._auth()

        output = await self._tb(["--no-version-warning", "sql", "SELECT 1"], env={'PYTEST': ""})

        expected = [FeedbackManager.warning_development_cli()]
        self._assert_feedback_output(expected, output, not_in=True)


class TestCLIFmt(TestCLI):
    @tornado.testing.gen_test
    async def test_datasource_fmt(self) -> None:
        await self._auth()

        (include_file, _) = self.create_tmp_file(suffix='.incl')
        include_file.write("""
KAFKA_CONNECTION_NAME my_connection_name
KAFKA_BOOTSTRAP_SERVERS my_server:9092
KAFKA_KEY my_username
KAFKA_SECRET my_password
""")

        (datasource_file, _) = self.create_tmp_file(suffix='.datasource')
        datasource_file.write(f"""
DESCRIPTION >
    This is a data source
VERSION 2

SCHEMA >
  cod_brand Int32,
  partnumber String,
  parent_partnumber String,
  global_parent_partnumber String,
  cod_product Int32,
  cod_section Int32,
  cod_product_line Int32,
  cod_family Int32,
  cod_subfamily Int32,
  description Nullable(String),
  image Nullable(String),
  plain_image Nullable(String),
  cod_campaign Int16,
  year_campaign Int16,
  season_campaign String,
  campaign String,
  cod_commercial_attr Int32,
  commercial_attr Nullable(String),
  product_line Nullable(String),
  section String,
  family String,
  subfamily String,
  model Int16,
  quality Int16,
  color Int16,
  product String,
  basic_price Float32,
  images Array(String),
  invoice_date Date,
  tags Array(String)



ENGINE "MergeTree"
ENGINE_SORTING_KEY "cod_section, cod_product"

INCLUDE "{include_file.name}"

KAFKA_TOPIC my_topic
KAFKA_GROUP_ID my_group_id

            """)
        datasource_file.seek(0)
        await self._tb(["fmt", datasource_file.name, '--yes'])

        expected = f"""VERSION 2

DESCRIPTION >
    This is a data source

SCHEMA >
    `cod_brand` Int32,
    `partnumber` String,
    `parent_partnumber` String,
    `global_parent_partnumber` String,
    `cod_product` Int32,
    `cod_section` Int32,
    `cod_product_line` Int32,
    `cod_family` Int32,
    `cod_subfamily` Int32,
    `description` Nullable(String),
    `image` Nullable(String),
    `plain_image` Nullable(String),
    `cod_campaign` Int16,
    `year_campaign` Int16,
    `season_campaign` String,
    `campaign` String,
    `cod_commercial_attr` Int32,
    `commercial_attr` Nullable(String),
    `product_line` Nullable(String),
    `section` String,
    `family` String,
    `subfamily` String,
    `model` Int16,
    `quality` Int16,
    `color` Int16,
    `product` String,
    `basic_price` Float32,
    `images` Array(String),
    `invoice_date` Date,
    `tags` Array(String)

ENGINE MergeTree
ENGINE_SORTING_KEY cod_section, cod_product

INCLUDE "{include_file.name}"

KAFKA_TOPIC my_topic
KAFKA_GROUP_ID my_group_id

"""
        with open(datasource_file.name) as f:
            f.seek(0)
            output = f.read()
            self.assertEqual(output, expected)

    @tornado.testing.gen_test
    async def test_pipe_fmt(self) -> None:
        await self._auth()

        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        datasource_file.write("""
VERSION 2

SCHEMA >
  cod_brand Int32,
  partnumber String,
  parent_partnumber String,
  global_parent_partnumber String,
  cod_product Int32,
  cod_section Int32,
  cod_product_line Int32,
  cod_family Int32,
  cod_subfamily Int32,
  description Nullable(String),
  image Nullable(String),
  plain_image Nullable(String),
  cod_campaign Int16,
  year_campaign Int16,
  season_campaign String,
  campaign String,
  cod_commercial_attr Int32,
  commercial_attr Nullable(String),
  product_line Nullable(String),
  section String,
  family String,
  subfamily String,
  model Int16,
  quality Int16,
  color Int16,
  product String,
  basic_price Float32,
  images Array(String),
  invoice_date Date,
  tags Array(String)

ENGINE "MergeTree"
ENGINE_SORTING_KEY "cod_section, cod_product"

            """)

        (include_file, _) = self.create_tmp_file(suffix='.incl')
        include_file.write(f"""
NODE node_included
DESCRIPTION >
    test
SQL >
  SELECT * from {datasource_name}
""")

        (pipe_file, _) = self.create_tmp_file(suffix='.pipe')
        pipe_file.write(f"""
VERSION 0

TOKEN "read_api" READ

NODE node_1
DESCRIPTION >
    whatever
SQL >
    SELECT 1

INCLUDE "{include_file.name}"

NODE articles_filters_view_gen
DESCRIPTION >
    whatever
SQL >
    %
    SELECT CAST(concat(toString(cod_brand), '_', toString(toInt32(substring(partnumber, 1, 1))), '_', toString(toInt32(substring(partnumber, 2, 4))), '_', toString(toInt32(substring(partnumber, 9, 3))), '_', toString(toInt32(substring(partnumber, 6, 3))), '-', right(partnumber, 5)), 'LowCardinality(String)') AS cb_sku_rank_lc, right(partnumber, 5) as campaign, cod_brand,
        partnumber,
        parent_partnumber,
        global_parent_partnumber,
        cod_product,
        cod_section,
        cod_product_line,
        cod_family,
        cod_subfamily,
        description,
        image,
        plain_image,
        invoice_date,
        invoice_date_1_16 == toDate(0) ? invoice_date: invoice_date_1_16 as invoice_date_1_16,
        tags
    FROM {datasource_name}
    LEFT JOIN (         SELECT partnumber, invoice_date as invoice_date_1_16
        FROM {{{{TABLE('test')}}}}
        WHERE cod_brand = 1
        AND invoice_date != '2000-01-01'
    ) USING partnumber
    WHERE length(partnumber) == 17



TYPE materialized
DATASOURCE articles_filters
""")

        expected = f"""VERSION 0

TOKEN "read_api" READ

NODE node_1
DESCRIPTION >
    whatever

SQL >
    SELECT 1

INCLUDE "{include_file.name}"


NODE articles_filters_view_gen
DESCRIPTION >
    whatever

SQL >
    %
    SELECT
        CAST(
            concat(
                toString(cod_brand),
                \'_\',
                toString(toInt32(substring(partnumber, 1, 1))),
                \'_\',
                toString(toInt32(substring(partnumber, 2, 4))),
                \'_\',
                toString(toInt32(substring(partnumber, 9, 3))),
                \'_\',
                toString(toInt32(substring(partnumber, 6, 3))),
                \'-\',
                right(partnumber, 5)
            ),
            \'LowCardinality(String)\'
        ) AS cb_sku_rank_lc,
        right(partnumber, 5) as campaign,
        cod_brand,
        partnumber,
        parent_partnumber,
        global_parent_partnumber,
        cod_product,
        cod_section,
        cod_product_line,
        cod_family,
        cod_subfamily,
        description,
        image,
        plain_image,
        invoice_date,
        invoice_date_1_16 == toDate(0) ? invoice_date:invoice_date_1_16 as invoice_date_1_16,
        tags
    FROM {datasource_name}
    LEFT JOIN
        (
            SELECT partnumber, invoice_date as invoice_date_1_16
            FROM {{{{ TABLE('test') }}}}
            WHERE cod_brand = 1 AND invoice_date != \'2000-01-01\'
        ) USING partnumber
    WHERE length(partnumber) == 17

TYPE MATERIALIZED
DATASOURCE articles_filters
"""

        pipe_file.seek(0)
        await self._tb(["fmt", pipe_file.name, '--yes'])

        with open(pipe_file.name) as f:
            f.seek(0)
            output = f.read()
            self.assertEqual(output, expected)

    @tornado.testing.gen_test
    async def test_include_fmt(self) -> None:
        await self._auth()

        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        datasource_file.write("""
VERSION 2

SCHEMA >
  cod_brand Int32,
  partnumber String,
  parent_partnumber String,
  global_parent_partnumber String,
  cod_product Int32,
  cod_section Int32,
  cod_product_line Int32,
  cod_family Int32,
  cod_subfamily Int32,
  description Nullable(String),
  image Nullable(String),
  plain_image Nullable(String),
  cod_campaign Int16,
  year_campaign Int16,
  season_campaign String,
  campaign String,
  cod_commercial_attr Int32,
  commercial_attr Nullable(String),
  product_line Nullable(String),
  section String,
  family String,
  subfamily String,
  model Int16,
  quality Int16,
  color Int16,
  product String,
  basic_price Float32,
  images Array(String),
  invoice_date Date,
  tags Array(String)

ENGINE "MergeTree"
ENGINE_SORTING_KEY "cod_section, cod_product"

            """)

        (include_file, _) = self.create_tmp_file(suffix='.incl')
        include_file.write(f"""
NODE node_included
DESCRIPTION >
    test
SQL >
  SELECT * from {datasource_name}
""")

        include_file.seek(0)
        await self._tb(["fmt", include_file.name, '--yes'])

        expected = f"""NODE node_included
DESCRIPTION >
    test

SQL >
    SELECT * from {datasource_name}

"""

        with open(include_file.name) as f:
            f.seek(0)
            output = f.read()
            self.assertEqual(output, expected)


class TestCLITest(TestCLI):
    @tornado.testing.gen_test
    async def test_run_test_file(self) -> None:
        await self._auth()

        test_file_content = """
                - this_test_should_fail:
                    sql: SELECT number FROM numbers(5) WHERE 1
                    max_time: null
                    max_bytes_read: null

                - this_test_should_pass:
                    sql: SELECT -number FROM numbers(5) WHERE 0
                    max_time: null
                    max_bytes_read: null

                - this_test_should_pass_over_time:
                    sql: SELECT * FROM numbers(500000000) WHERE 0
                    max_time: 0.0000001
                    max_bytes_read: null

                - this_test_should_pass_over_bytes:
                    sql: SELECT sum(number) AS total FROM numbers(5) HAVING total>1000
                    max_time: null
                    max_bytes_read: 5

                - this_test_should_pass_over_time_and_bytes:
                    sql: SELECT * FROM numbers(500000000) WHERE number < 0
                    max_time: 0.0000001
                    max_bytes_read: 5

                - a_multiline_test:
                    sql: SELECT
                        -number
                        FROM numbers(5)
                        WHERE 0
                    max_time: null

                - error_test_wrong_sql:
                    sql: SELECT
                    max_time: null

                - error_test_no_sql:
                    max_time: null
            """

        (test_file, _) = self.create_tmp_file(suffix='.yaml')
        test_file.write(test_file_content)
        test_file.seek(0)

        output = await self._tb(["test", "run", test_file.name],
                                assert_exit_code=1)

        expected = [
            f"{test_file.name} | this_test_should_fail                     | Fail",
            f"{test_file.name} | this_test_should_pass                     | Pass",
            f"{test_file.name} | this_test_should_pass_over_time           | Pass Over Time",
            f"{test_file.name} | this_test_should_pass_over_bytes          | Pass Over Read Bytes",
            f"{test_file.name} | this_test_should_pass_over_time_and_bytes | Pass Over Time and Over Read Bytes",
            f"{test_file.name} | a_multiline_test                          | Pass",
            f"{test_file.name} | error_test_wrong_sql                      | Error",
            f"{test_file.name} | error_test_no_sql                         | Error",
            "Totals:",
            "Total Fail: 1",
            "Total Pass: 2",
            "Total Pass Over Time: 1",
            "Total Pass Over Read Bytes: 1",
            "Total Error: 2",
            FeedbackManager.error_some_data_validation_have_failed()
        ]
        self._assert_feedback_output(expected, output)

        (test_file, _) = self.create_tmp_file(suffix='.yaml')
        output = await self._tb(["test", "init", "--force", test_file.name])
        expected = [
            FeedbackManager.success_generated_local_file(file=test_file.name)
        ]
        self._assert_feedback_output(expected, output)

        output = await self._tb(["test", "run", test_file.name],
                                assert_exit_code=1)
        expected = [
            f"{test_file.name} | this_test_should_fail                     | Fail",
            f"{test_file.name} | this_test_should_pass                     | Pass",
            f"{test_file.name} | this_test_should_pass_over_time           | Pass Over Time",
            f"{test_file.name} | this_test_should_pass_over_bytes          | Pass Over Read Bytes",
            f"{test_file.name} | this_test_should_pass_over_time_and_bytes | Pass Over Time and Over Read Bytes",
            "Totals:",
            "Total Pass: 1",
            "Total Fail: 1",
            "Total Pass Over Time: 1",
            "Total Pass Over Read Bytes: 1",
            "Total Pass Over Time and Over Read Bytes: 1",
            FeedbackManager.error_some_data_validation_have_failed()
        ]
        self._assert_feedback_output(expected, output)

        output = await self._tb(["test", "run", test_file.name, "--fail"],
                                assert_exit_code=1)
        expected = [
            f"{test_file.name} | this_test_should_fail                     | Fail",
            f"{test_file.name} | this_test_should_pass_over_time           | Pass Over Time",
            f"{test_file.name} | this_test_should_pass_over_bytes          | Pass Over Read Bytes",
            f"{test_file.name} | this_test_should_pass_over_time_and_bytes | Pass Over Time and Over Read Bytes",
            "Totals:",
            "Total Pass: 1",
            "Total Fail: 1",
            "Total Pass Over Time: 1",
            "Total Pass Over Read Bytes: 1",
            "Total Pass Over Time and Over Read Bytes: 1",
            FeedbackManager.error_some_data_validation_have_failed()
        ]
        self._assert_feedback_output(expected, output)

        not_expected = [
            f"{test_file.name} | this_test_should_pass                     | Pass",
        ]
        self._assert_feedback_output(expected, output)
        self._assert_feedback_output(not_expected, output, not_in=True)


class TestCLIDiff(TestCLI):
    @tornado.testing.gen_test
    async def test_diff_local_file(self) -> None:
        await self._auth()

        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        (pipe_file, _) = self.create_tmp_file(suffix='.pipe')

        datasource_file.write("""
VERSION 0

SCHEMA >
`a1` Int64,
`a2` String,
`a3` String

ENGINE "MergeTree"
        """)
        datasource_file.seek(0)
        await self._tb(["push", datasource_file.name])

        pipe_file.write(f"""
VERSION 1

DESCRIPTION >
    This is a description

NODE mv
SQL >

    SELECT
        a1,
        a2,
        a3
    FROM {datasource_name}
            """)

        pipe_file.seek(0)
        await self._tb(["push", pipe_file.name])

        pipe_file.write(f"""
VERSION 1

DESCRIPTION >
    This is a description

NODE mv
SQL >

    SELECT
        2 as a1,
        a2,
        a3
    FROM {datasource_name}
            """)
        pipe_file.seek(0)

        # diff of a single file
        output = await self._tb(["diff", pipe_file.name, "--no-color"])
        expected = [
            f'NODE mv SQL >-    SELECT a1, a2, a3 FROM {datasource_name}+    SELECT 2 as a1, a2, a3 FROM {datasource_name}',
        ]
        self._assert_feedback_output(expected, output)

        # diff of a single file with fmt
        output = await self._tb(["diff", pipe_file.name, "--no-color"])
        self.assertTrue(f'NODE mv SQL >-    SELECT a1, a2, a3 FROM {datasource_name}+    SELECT 2 as a1, a2, a3 FROM {datasource_name}' in output)

        # diff workspace
        file = self._get_resource_path('test_ds_engine_ttl.datasource')
        await self._tb(["push", file])
        output = await self._tb(["diff", "--no-color"])
        self.assertTrue('test_ds_engine_ttl only exists in remote' in output)

    @tornado.testing.gen_test
    async def test_diff_local_file_with_include(self) -> None:
        await self._auth()
        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        (pipe_file, _) = self.create_tmp_file(suffix='.pipe')

        datasource_file.write("""
VERSION 0

SCHEMA >
`a1` Int64,
`a2` String,
`a3` String

ENGINE "MergeTree"
        """)
        datasource_file.seek(0)
        await self._tb(["push", datasource_file.name])

        pipe_file.write(f"""
VERSION 1

DESCRIPTION >
    This is a description

NODE mv
SQL >

    SELECT
        a1,
        a2,
        a3
    FROM {datasource_name}
            """)

        pipe_file.seek(0)
        await self._tb(["push", pipe_file.name])

        (include_file, _) = self.create_tmp_file(suffix='.incl')
        include_file.write("""
NODE included_node
SQL >
    SELECT 1
""")
        include_file.seek(0)

        pipe_file.write(f"""
VERSION 1

NODE mv
SQL >

    SELECT
        a1,
        a2,
        a3
    FROM {datasource_name}

INCLUDE {include_file.name}
            """)
        pipe_file.seek(0)
        output = await self._tb(["diff", pipe_file.name, "--no-color"])
        expected = [
            f'SQL >     SELECT a1, a2, a3 FROM {datasource_name} +NODE included_node+SQL >+    SELECT 1',
        ]

        self._assert_feedback_output(expected, output)

    @tornado.testing.gen_test
    async def test_diff_local_file_with_connector(self) -> None:
        await self._auth()
        (connector_file, _) = self.create_tmp_file(suffix='.incl')
        connector_file.write("""
KAFKA_CONNECTION_NAME connection_name
KAFKA_BOOTSTRAP_SERVERS tinybird.co:80
KAFKA_KEY aaa
KAFKA_SECRET bbb
KAFKA_TOPIC ttt
KAFKA_GROUP_ID ggg
KAFKA_STORE_RAW_VALUE 'True'""")
        connector_file.seek(0)

        (datasource_file, datasource_name) = self.create_tmp_file(suffix='.datasource')
        datasource_file.write(f"""
VERSION 0

TOKEN "whatever" APPEND

SCHEMA >
    `__value` String

ENGINE "MergeTree"
ENGINE_PARTITION_KEY "toYYYYMM(__timestamp)"
ENGINE_SORTING_KEY "__timestamp"
ENGINE_TTL "__timestamp + INTERVAL 1 day"

INCLUDE "{connector_file.name}"
""")
        datasource_file.seek(0)
        connector_file.seek(0)
        with patch.object(KafkaUtils, 'get_kafka_topic_group', return_value={'response': 'ok'}):
            output = await self._tb(["push", datasource_file.name])
            self.assertTrue(f"'{datasource_name}__v0' created" in output)

        output = await self._tb(["diff", datasource_file.name, "--no-color"])
        self.assertTrue('-ENGINE_TTL __timestamp + toIntervalDay(1)+ENGINE_TTL __timestamp + INTERVAL 1 day' in output)

        connector_file.write("""
KAFKA_CONNECTION_NAME connection_name2
KAFKA_BOOTSTRAP_SERVERS tinybird.co:80
KAFKA_KEY aaa
KAFKA_SECRET bbb
KAFKA_TOPIC ttt
KAFKA_GROUP_ID ggg
KAFKA_STORE_RAW_VALUE 'True'""")
        connector_file.seek(0)

        output = await self._tb(["diff", datasource_file.name, "--no-color"])
        # we don't diff changes in the KAFKA config by default, we assume it's immutable
        self.assertTrue('-ENGINE_TTL __timestamp + toIntervalDay(1)+ENGINE_TTL __timestamp + INTERVAL 1 day' in output)


class TestCLITelemetry(TestCLI):

    @tornado.testing.gen_test
    async def test_collect_events(self) -> None:
        events: List[Dict[str, Any]] = []

        env: Dict[str, str] = {
            'TB_CLI_TELEMETRY_OPTOUT': '0',
            'TB_CLI_TELEMETRY_SEND_IN_LOCAL': '1'
        }

        helper = get_telemetry_helper()
        helper.max_enqueued_events = 100000  # Avoid calling flush during tests

        def mock_flush(wait: bool = False) -> None:
            for e in helper.events:
                events.append(e)

        def event_count(event_type: str) -> int:
            return sum(1 for e in events if e['event'] == event_type)

        with patch.object(helper, 'flush', mock_flush):
            await self._auth(env=env)
            flush_telemetry(wait=True)
            self.assertEqual(event_count('auth_token'), 1)
            self.assertEqual(event_count('api_request'), 1)
            self.assertEqual(event_count('auth_success'), 1)
            events.clear()

            _ = self._tb(['workspace', 'ls'], env=env)
            flush_telemetry(wait=True)
            self.assertEqual(event_count('api_request'), 1)
            events.clear()

    @tornado.testing.gen_test
    async def test_no_collect_events_if_optout(self) -> None:
        env: Dict[str, str] = {
            'TB_CLI_TELEMETRY_OPTOUT': '1',
            'TB_CLI_TELEMETRY_SEND_IN_LOCAL': '1'
        }

        helper = get_telemetry_helper()
        helper.max_enqueued_events = 0  # Force calling flush on the first event

        def mock_flush(wait: bool = False) -> None:
            raise AssertionError("Flush was called")

        with patch.object(helper, 'flush', mock_flush):
            await self._auth(env=env)
            flush_telemetry(wait=True)

    @tornado.testing.gen_test
    async def test_no_collect_events_if_local(self) -> None:
        env: Dict[str, str] = {
            'TB_CLI_TELEMETRY_OPTOUT': '0',
            'TB_CLI_TELEMETRY_SEND_IN_LOCAL': '0'
        }

        helper = get_telemetry_helper()
        helper.max_enqueued_events = 0  # Force calling flush on the first event

        def mock_flush(wait: bool = False) -> None:
            raise AssertionError("Flush was called")

        with patch.object(helper, 'flush', mock_flush):
            await self._auth(env=env)
            flush_telemetry(wait=True)
