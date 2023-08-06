from typing import Any, Dict, List
import unittest.mock
import uuid

import tornado.testing

from tinybird.auth0_client import Auth0Client
from tinybird.redis_client import get_redis_test_client
from tinybird.useraccounts_service import UserAccountsService
from tinybird.user import UserAccount


def patch_get_users_by_email(data: Dict[str, Any]) -> Dict[str, Any]:
    return unittest.mock.patch.object(Auth0Client, 'get_users_by_email', return_value=data)


class TestUserAccountsService(tornado.testing.AsyncTestCase):

    def setUp(self):
        super(TestUserAccountsService, self).setUp()
        self.users_to_delete: List[UserAccount] = []
        self.redis_client = get_redis_test_client()

    def tearDown(self):
        for u in self.users_to_delete:
            UserAccount._delete(u.id)
        super(TestUserAccountsService, self).tearDown()

    def _create_user(self, email: str = None) -> UserAccount:
        email = email if email else f'test_{uuid.uuid4().hex}@example.com'
        user = UserAccount.register(email, 'pass')
        self.users_to_delete.append(user)
        return user

    @tornado.testing.gen_test
    async def test_get_auth_provider_info(self):
        new_user = self._create_user()

        with patch_get_users_by_email([{'logins_count': 4}, {'logins_count': 1}]):
            info = await UserAccountsService.get_auth_provider_info(new_user)
            self.assertEqual(info['logins_count'], 5)

        with patch_get_users_by_email([{'logins_count': 0}, {'logins_count': 0}]):
            info = await UserAccountsService.get_auth_provider_info(new_user)
            self.assertEqual(info['logins_count'], 0)

        with patch_get_users_by_email([{'logins_count': 42}]):
            info = await UserAccountsService.get_auth_provider_info(new_user)
            self.assertEqual(info['logins_count'], 42)

        with patch_get_users_by_email([]):
            info = await UserAccountsService.get_auth_provider_info(new_user)
            self.assertEqual(info['logins_count'], 0)
