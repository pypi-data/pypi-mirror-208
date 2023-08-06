import asyncio
import tornado

from tests.views.base_test import BaseTest
from tests_e2e.aux import poll_async
from tinybird.async_redis import async_redis_writer
from tinybird.redis_client import get_redis_config

from datetime import datetime, timezone
from io import StringIO
from unittest.mock import AsyncMock

import aiohttp
from tinybird.user import Users
from tinybird.token_scope import scopes
from tinybird.ingestion_observer import INGESTION_LAGGY_WINDOW, INGESTION_OBSERVER_POLL_SECONDS, IngestionObserver
from .conftest import is_main_process
import pytest


@pytest.mark.serial  # Better to test this serially
@pytest.mark.skipif(not is_main_process(), reason="Serial test")
class TestIncident(BaseTest):
    @tornado.testing.gen_test
    async def test_ingest_incident_ndjson_url_failed(self):
        ds_id = None

        async def provoke_incident():
            nonlocal ds_id
            u = Users.get_by_id(self.WORKSPACE_ID)
            token = Users.get_token_for_scope(u, scopes.ADMIN)
            headers = {'Authorization': f"Bearer {token}"}
            ds_name = 'test_ingest_incident_ndjson_url_failed'
            async with aiohttp.request('POST', self.get_url('/v0/datasources'),
                                       headers=headers,
                                       params={
                                       'mode': 'create',
                                       'name': ds_name,
                                       'format': 'ndjson',
                                       'schema': "date DateTime('UTC') `json:$.date`, city String `json:$.extra_data.city`",
                                       'url': self.get_url('/not_exists.ndjson'),
                                       }) as r:
                self.assertEqual(r.status, 200, await r.json())
                ds_id = (await r.json())['job']['datasource']['id']

        async def check_mailgun_mock(mailgun_mock):
            nonlocal ds_id
            assert mailgun_mock.send_notification_on_ingestion_incident.call_count == 1
            call_args = mailgun_mock.send_notification_on_ingestion_incident.call_args.args
            assert '@example.com' in call_args[0][0]
            assert call_args[2].id == ds_id
            assert call_args[3]['status'] == 'new'
            assert '404' in call_args[3]['errors'][0]
            assert call_args[3]['next_timestamp'] == 0

        await self._test_incident(provoke_incident, check_mailgun_mock)

    @tornado.testing.gen_test
    async def test_ingest_quarantine_incident(self):
        ds_id = None

        async def provoke_incident():
            nonlocal ds_id
            u = Users.get_by_id(self.WORKSPACE_ID)
            token = Users.get_token_for_scope(u, scopes.ADMIN)
            headers = {'Authorization': f"Bearer {token}"}
            ds_name = 'test_ingest_quarantine_incident'
            async with aiohttp.request('POST', self.get_url('/v0/datasources'),
                                       headers=headers,
                                       params={
                                       'mode': 'create',
                                       'name': ds_name,
                                       'schema': 'col_a Int32,col_b Int32,col_c Int8',
                                       }) as r:
                self.assertEqual(r.status, 200, await r.json())
                ds_id = (await r.json())['datasource']['id']
            params = {
                'mode': 'append',
                'token': token,
                'name': ds_name,
            }
            data = StringIO('a,b,3\n4,d,6\n7,h,j')
            async with aiohttp.request('POST', self.get_url('/v0/datasources'),
                                       headers=headers,
                                       params=params,
                                       data=data) as r:
                assert r.status == 200

        async def check_mailgun_mock(mailgun_mock):
            nonlocal ds_id
            assert mailgun_mock.send_notification_on_quarantine_incident.call_count == 1
            call_args = mailgun_mock.send_notification_on_quarantine_incident.call_args.args
            assert '@example.com' in call_args[0][0]
            assert call_args[2].id == ds_id
            assert call_args[3]['status'] == 'new'
            assert call_args[3]['imports'] == 1
            assert call_args[3]['rows'] == 3
            assert call_args[3]['next_timestamp'] == 0

        await self._test_incident(provoke_incident, check_mailgun_mock)

    async def _test_incident(self, provoke_incident, check_mailgun_mock):
        redis_config = get_redis_config({'port': None})
        async_redis_writer.init(redis_config)
        mailgun_mock = AsyncMock()
        ingestion_observer = IngestionObserver(mailgun_mock)

        async def f():
            last_check = int(datetime.now(timezone.utc).timestamp()) - 2 * INGESTION_OBSERVER_POLL_SECONDS
            return True, last_check

        ingestion_observer._should_check_for_incidents = f
        await ingestion_observer.run()
        try:
            await provoke_incident()
            await asyncio.sleep(INGESTION_LAGGY_WINDOW)

            async def f():
                await check_mailgun_mock(mailgun_mock)

            await poll_async(f)
        finally:
            await ingestion_observer.terminate()
            await async_redis_writer.reset()
