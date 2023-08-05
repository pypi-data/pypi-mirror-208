import unittest
import uuid

from tinybird.hook import Hook
from tinybird.user import User, UserAccount


class BaseTestHook(Hook):
    def __init__(self, user):
        super().__init__(user)
        self.called_before_create = False
        self.called_after_create = False
        self.called_tear_down = False
        self.called_on_error = False
        self.captured_error = None

    def on_error(self, datasource, error):
        self.called_on_error = True
        self.captured_error = error

    def tear_down(self, datasource):
        self.called_tear_down = True


class HappyCaseHook(BaseTestHook):

    def before_create(self, datasource):
        self.called_before_create = True

    def after_create(self, datasource):
        self.called_after_create = True
        self.tear_down(datasource)


class AfterCreateFailsHook(BaseTestHook):

    def before_create(self, datasource):
        self.called_before_create = True

    def after_create(self, datasource):
        self.called_after_create = True
        raise RuntimeError('Failed before tear_down')


class TestHooks(unittest.TestCase):

    def setUp(self):
        self.WORKSPACE = f'test_hooks_{uuid.uuid4().hex}'
        self.USER = f'{self.WORKSPACE}@example.com'

        self.user = UserAccount.register(self.USER, 'pass')
        self.workspace = User.register(
            name=self.WORKSPACE,
            admin=self.user.id
        )

    def tearDown(self):
        User._delete(self.workspace.id)
        user_account = UserAccount.get_by_email(self.USER)
        UserAccount._delete(user_account.id)

    def test_happy_case(self):
        ds = self.workspace.add_datasource('fake_datasource')

        hook = HappyCaseHook(self.workspace)
        ds.install_hook(hook)

        try:
            for h in ds.hooks:
                h.before_create(ds)

            for h in ds.hooks:
                h.after_create(ds)
        except Exception:
            for h in ds.hooks:
                h.on_error(ds)

        self.assertTrue(hook.called_before_create)
        self.assertTrue(hook.called_after_create)
        self.assertTrue(hook.called_tear_down)
        self.assertFalse(hook.called_on_error)

    def test_after_create_fails_but_tear_down_still_called(self):
        ds = self.workspace.add_datasource('fake_datasource')

        hook = AfterCreateFailsHook(self.workspace)
        ds.install_hook(hook)

        try:
            for h in ds.hooks:
                h.before_create(ds)

            for h in ds.hooks:
                h.after_create(ds)
        except Exception as e:
            self.assertEqual(hook.captured_error, e)

        self.assertTrue(hook.called_before_create)
        self.assertTrue(hook.called_after_create)
        self.assertTrue(hook.called_tear_down)
        self.assertTrue(hook.called_on_error)

    def test_after_create_two_hooks_fails_first(self):
        ds = self.workspace.add_datasource('fake_datasource')

        fails_hook = AfterCreateFailsHook(self.workspace)
        ds.install_hook(fails_hook)
        happy_hook = HappyCaseHook(self.workspace)
        ds.install_hook(happy_hook)

        try:
            for h in ds.hooks:
                h.before_create(ds)

            for h in ds.hooks:
                h.after_create(ds)
        except Exception as e:
            self.assertEqual(fails_hook.captured_error, e)
            for h in ds.hooks:
                h.on_error(ds, e)

        self.assertTrue(fails_hook.called_before_create)
        self.assertTrue(fails_hook.called_after_create)
        self.assertTrue(fails_hook.called_tear_down)
        self.assertTrue(fails_hook.called_on_error)

        self.assertTrue(happy_hook.called_before_create)
        self.assertFalse(happy_hook.called_after_create)
        self.assertTrue(happy_hook.called_tear_down)
        self.assertTrue(happy_hook.called_on_error)
