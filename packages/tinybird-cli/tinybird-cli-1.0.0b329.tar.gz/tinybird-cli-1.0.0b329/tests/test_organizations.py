import asyncio
from typing import Any, Dict, Iterable, Optional
import tornado
import uuid

from tinybird.organization.organization import Organization, OrganizationCommitmentsPlans, Organizations
from tinybird.user import UserAccount, User, UserAccountAlreadyBelongsToOrganization, WorkspaceAlreadyBelongsToOrganization

from .views.base_test import BaseTest


class TestOrganizations(BaseTest):
    def setUp(self) -> None:
        self.organizations_to_delete = []
        super().setUp()

    def tearDown(self) -> None:
        for org in self.organizations_to_delete:
            asyncio.run(Organizations.remove_organization(org))
        super().tearDown()

    def _create_user(self, prefix: str) -> UserAccount:
        email: str = f'{prefix}_{uuid.uuid4().hex}@example.com'
        result: UserAccount = UserAccount.register(email, 'pass')
        self.users_to_delete.append(result)
        return result

    def _create_workspace(self, prefix: str, user: UserAccount) -> User:
        workspace_name: str = f'workspace_{prefix}_{uuid.uuid4().hex}'
        result: User = User.register(workspace_name, user.id)
        self.workspaces_to_delete.append(result)
        return result

    async def _create_organization(self, name: str, domain: Optional[str] = None,
                                   plan_details: Optional[Dict[str, Any]] = None,
                                   workspace_ids: Optional[Iterable[str]] = None,
                                   user_ids: Optional[Iterable[str]] = None) -> Organization:
        org = Organization.create(name)
        self.organizations_to_delete.append(org)

        if domain:
            org = await Organizations.update_name_and_domain(org, name, domain)

        if plan_details:
            org = await Organizations.update_commitment_information(
                org,
                start_date=plan_details['start_date'],
                end_date=plan_details['end_date'],
                commited_processed=plan_details['commitment']['processed'],
                commited_storage=plan_details['commitment']['storage'],
                commitment_billing=plan_details['billing']
            )

        if workspace_ids:
            for id in workspace_ids:
                org = await Organizations.add_workspace(org, User.get_by_id(id))

        if user_ids:
            for id in user_ids:
                org = await Organizations.add_user(org, UserAccount.get_by_id(id))

        return org

    @tornado.testing.gen_test
    async def test_create_organization(self) -> None:
        """Tests a new Organization defaults.
        """
        user = self._create_user('test_create_organization')
        workspace = self._create_workspace('test_create_organization', user)
        org = await self._create_organization('test_create_organization',
                                              user_ids=[user.id],
                                              workspace_ids=[workspace.id])
        # Linked users and workspaces
        self.assertEqual(UserAccount.get_by_id(user.id).organization_id, org.id)
        self.assertEqual(User.get_by_id(workspace.id).organization_id, org.id)

        # Metadata
        self.assertEqual(org.name, 'test_create_organization')
        self.assertEqual(org.domain, None)
        self.assertEqual(org.plan_details['name'], '')
        self.assertNotEqual(org.plan_details['start_date'], '')
        self.assertEqual(org.plan_details['end_date'], '')
        self.assertEqual(org.plan_details['commitment']['storage'], 0)
        self.assertEqual(org.plan_details['commitment']['processed'], 0)
        self.assertEqual(org.plan_details['billing'], OrganizationCommitmentsPlans.TOTAL_USAGE)

    @tornado.testing.gen_test
    async def test_remove_organization(self) -> None:
        """Test the removal of an organization successfully unlinks
           all linked users and workspaces.
        """
        user = self._create_user('test_create_organization')
        workspace = self._create_workspace('test_create_organization', user)
        org = await self._create_organization('test_create_organization',
                                              user_ids=[user.id],
                                              workspace_ids=[workspace.id])
        await Organizations.remove_organization(org)

        self.assertEqual(UserAccount.get_by_id(user.id).organization_id, None)
        self.assertEqual(User.get_by_id(workspace.id).organization_id, None)

    @tornado.testing.gen_test
    async def test_update_meta(self) -> None:
        """Test the metadata update methods.
        """
        org = await self._create_organization('test_update_meta')

        org = await Organizations.update_name_and_domain(org, 'new_name', 'example.com')
        self.assertEqual(org.name, 'new_name')
        self.assertEqual(org.domain, 'example.com')

        org = await Organizations.update_commitment_information(org, '2100-01-01', '2100-12-31',
                                                                999, 666,
                                                                OrganizationCommitmentsPlans.NO_USAGE_COMMITMENT)
        self.assertEqual(org.plan_details['start_date'], '2100-01-01')
        self.assertEqual(org.plan_details['end_date'], '2100-12-31')
        self.assertEqual(org.plan_details['commitment']['storage'], 666)
        self.assertEqual(org.plan_details['commitment']['processed'], 999)
        self.assertEqual(org.plan_details['billing'], OrganizationCommitmentsPlans.NO_USAGE_COMMITMENT)

    @tornado.testing.gen_test
    async def test_add_workspace(self) -> None:
        """Tests we can't add the same workspace to two organizations.
        """
        user = self._create_user('test_add_workspace')
        workspace = self._create_workspace('test_add_workspace', user)
        org = await self._create_organization('test_add_workspace', workspace_ids=[workspace.id])
        self.assertEqual(len(org.workspace_ids), 1)

        try:
            _ = await self._create_organization('test_add_workspace_2', workspace_ids=[workspace.id])
            self.assertTrue(False, "We can't add a workspace to two organizations")
        except WorkspaceAlreadyBelongsToOrganization as ex:
            self.assertEqual(ex.workspace_id, workspace.id)
            self.assertEqual(ex.organization_id, org.id)

    @tornado.testing.gen_test
    async def test_remove_workspace(self) -> None:
        """Tests the removal of a workspace.
        """
        user = self._create_user('test_add_workspace')
        workspace = self._create_workspace('test_add_workspace', user)
        org = await self._create_organization('test_add_workspace', workspace_ids=[workspace.id])
        self.assertEqual(len(org.workspace_ids), 1)
        org = await Organizations.remove_workspace(org, workspace)
        self.assertEqual(len(org.workspace_ids), 0)
        self.assertEqual(User.get_by_id(workspace.id).organization_id, None)

    @tornado.testing.gen_test
    async def test_add_user(self) -> None:
        """Tests we can't add the same user to two organizations.
        """
        user = self._create_user('test_add_user')
        org = await self._create_organization('test_add_user', user_ids=[user.id])
        self.assertEqual(len(org.user_account_ids), 1)

        try:
            _ = await self._create_organization('test_add_user_2', user_ids=[user.id])
            self.assertTrue(False, "We can't add an user to two organizations")
        except UserAccountAlreadyBelongsToOrganization as ex:
            self.assertEqual(ex.user_id, user.id)
            self.assertEqual(ex.organization_id, org.id)

    @tornado.testing.gen_test
    async def test_remove_user(self) -> None:
        """Tests the removal of an user.
        """
        user = self._create_user('test_remove_user')
        org = await self._create_organization('test_remove_user', user_ids=[user.id])
        self.assertEqual(len(org.user_account_ids), 1)
        org = await Organizations.remove_user(org, user)
        self.assertEqual(len(org.user_account_ids), 0)
        self.assertEqual(UserAccount.get_by_id(user.id).organization_id, None)

    @tornado.testing.gen_test
    async def test_refresh_token(self) -> None:
        """Tests the observability token refresh.
        """
        user = self._create_user('test_refresh_token')
        org = await self._create_organization('test_refresh_token', user_ids=[user.id])
        token = org.token_observability.token
        org, refreshed = await Organizations.refresh_token(org, token)
        self.assertNotEqual(token, refreshed)

    @tornado.testing.gen_test
    async def test_refresh_invalid_token(self) -> None:
        """Tests the observability token is NOT refreshed by error.
        """
        user = self._create_user('test_refresh_invalid_token')
        org = await self._create_organization('test_refresh_invalid_token', user_ids=[user.id])
        token = org.token_observability.token
        org, refreshed = await Organizations.refresh_token(org, 'this_token_does_not_exist')
        self.assertEqual(refreshed, None)
        self.assertEqual(token, org.token_observability.token)
