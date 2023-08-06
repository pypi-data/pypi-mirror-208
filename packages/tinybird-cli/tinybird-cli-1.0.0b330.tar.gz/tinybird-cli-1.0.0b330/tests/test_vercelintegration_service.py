import json
from typing import cast
import tornado
from tinybird.integrations.vercel import VercelIntegration, VercelIntegrationException, VercelIntegrationPhase, VercelIntegrationService
from tinybird.token_scope import scopes

from tinybird.user import User, UserAccount, UserAccounts
from .views.base_test import BaseTest, TBApiProxyAsync, TBApiProxy

from unittest.mock import patch


class TestVercelIntegrationService(BaseTest):
    def setUp(self):
        super(TestVercelIntegrationService, self).setUp()
        self.tb_api_proxy_async: TBApiProxyAsync = TBApiProxyAsync(self)
        self.tb_api_proxy: TBApiProxy = TBApiProxy(self)
        self.user_account: UserAccount = UserAccount.get_by_id(self.USER_ID)

    async def reset_user(self) -> None:
        integrations = self.user_account.get_integrations()
        if not len(integrations):
            return
        integration = integrations[0]
        self.user_account = await VercelIntegrationService.remove_integration(self.user_account,
                                                                              integration.id,
                                                                              remove_remote=False)

    async def _create_integration(self) -> VercelIntegration:
        integration = await VercelIntegrationService.get_integration_for_user(self.user_account, 'dummy_access_code')
        assert integration.access_code
        assert integration.integration_phase == VercelIntegrationPhase.INSTALLING

        self.user_account = await UserAccounts.add_integration(self.user_account, 'vercel', integration.id)
        assert len(self.user_account.get_integration_info_by_type('vercel')) == 1
        return integration

    async def _finalize_install(self, integration: VercelIntegration) -> VercelIntegration:
        api_mock: str = json.dumps({
            "token_type": "Bearer",
            "access_token": "xEbuzM1ZAJ46afITQlYqH605",
            "installation_id": "icfg_ijgU3GzRxyz7nGpwwsSmbNkI",
            "user_id": "2tUzTmv4ljvFVHifEf9TGdpH",
            "team_id": None
        })

        with patch.object(VercelIntegrationService, '_vercel_post', return_value=(200, api_mock)):
            integration = await VercelIntegrationService.finalize_install(integration)
            assert not integration.access_code
            assert integration.integration_phase == VercelIntegrationPhase.CONFIGURED
            return integration

    @tornado.testing.gen_test
    async def test_create(self) -> None:
        await self.reset_user()
        _ = await self._create_integration()

    @tornado.testing.gen_test
    async def test_create_and_finalize(self) -> None:
        await self.reset_user()
        integration = await self._create_integration()
        installed = await self._finalize_install(integration)
        assert installed.id == integration.id

    @tornado.testing.gen_test
    async def test_create_and_finalize_twice(self) -> None:
        await self.reset_user()
        integration = await self._create_integration()
        installed = await self._finalize_install(integration)
        assert not installed.access_code
        assert installed.integration_phase == VercelIntegrationPhase.CONFIGURED

    @tornado.testing.gen_test
    async def test_create_and_fetch(self) -> None:
        await self.reset_user()
        integration = await self._create_integration()
        dummy = await VercelIntegrationService.get_integration_for_user(self.user_account)
        assert dummy.id == integration.id

    @tornado.testing.gen_test
    async def test_add_binding(self) -> None:
        await self.reset_user()
        integration = await self._create_integration()
        integration = await self._finalize_install(integration)

        workspace = User.get_by_id(self.WORKSPACE_ID)
        tk: str = cast(str, workspace.get_token_for_scope(scopes.ADMIN))

        with patch.object(VercelIntegrationService, '_vercel_post', return_value=(200, '{}')):
            integration = await VercelIntegrationService.add_bindings(integration, 'test_project', self.WORKSPACE_ID, [tk])
            assert len(integration.get_bindings()) == 1

        with patch.object(VercelIntegrationService, '_vercel_post', return_value=(200, '{}')):
            try:
                integration = await VercelIntegrationService.add_bindings(integration, 'test_project', self.WORKSPACE_ID, ['unknown_token'])
            except VercelIntegrationException:
                pass
            assert len(integration.get_bindings()) == 1
