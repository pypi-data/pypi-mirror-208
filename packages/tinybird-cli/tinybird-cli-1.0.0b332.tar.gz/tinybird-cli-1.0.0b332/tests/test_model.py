import threading
from collections import defaultdict

import unittest
from unittest.mock import patch
import uuid
from dataclasses import dataclass

import tornado.testing
from tornado.testing import AsyncTestCase

from tinybird.job import Job
from tinybird.model import retry_transaction_in_case_of_concurrent_edition_error_sync, ConcurrentEditionException, \
    retry_transaction_in_case_of_concurrent_edition_error_async, RedisModel, ModelLRUCache
from tests.test_jobs import FakeTestJob
from tinybird.user import User, UserAccount
from tinybird.redis_client import get_redis_test_client


class FailsBeforeSuccess:
    def __init__(self, fails):
        self.fails = fails


class TestRetryInCaseOfConcurrentEditionError(AsyncTestCase):
    def setUp(self):
        super().setUp()
        workspace_name = f'testing_model_{uuid.uuid4().hex}'
        user_email = f'{workspace_name}@example.com'

        self.user = UserAccount.register(user_email, 'pass')
        self.workspace = User.register(workspace_name, admin=self.user.id)
        self.workspace.database = 'default'
        self.workspace.save()

    def tearDown(self):
        User._delete(self.workspace.id)
        super().tearDown()

    def test_correctly_finished_after_some_retries(self):
        job = FakeTestJob(self.workspace)
        job.save()

        @retry_transaction_in_case_of_concurrent_edition_error_sync(tries=10, delay=0.001, backoff=1)
        def semi_mocked_function_with_some_retries(fail_before_success):
            with Job.transaction(job.id) as j:
                if fail_before_success.fails != 0:
                    print(fail_before_success.fails)
                    fail_before_success.fails -= 1
                    j.save()
            return fail_before_success.fails

        remaining_fails = semi_mocked_function_with_some_retries(FailsBeforeSuccess(8))
        self.assertEqual(remaining_fails, 0)

    def test_raises_runtime_error_if_it_fails_more_than_the_configured_retries(self):
        job = FakeTestJob(self.workspace)
        job.save()

        @retry_transaction_in_case_of_concurrent_edition_error_sync(tries=3, delay=0.001, backoff=1)
        def semi_mocked_function_with_some_retries(fail_before_success):
            with Job.transaction(job.id) as j:
                if fail_before_success.fails != 0:
                    print(fail_before_success.fails)
                    fail_before_success.fails -= 1
                    j.save()

        with self.assertRaises(ConcurrentEditionException):
            semi_mocked_function_with_some_retries(FailsBeforeSuccess(5))

    @tornado.testing.gen_test
    async def test_correctly_finished_after_some_retries_async(self):
        job = FakeTestJob(self.workspace)
        job.save()

        @retry_transaction_in_case_of_concurrent_edition_error_async(tries=10, delay=0.001, backoff=1)
        async def semi_mocked_function_with_some_retries(fail_before_success):
            with Job.transaction(job.id) as j:
                if fail_before_success.fails != 0:
                    print(fail_before_success.fails)
                    fail_before_success.fails -= 1
                    j.save()
            return fail_before_success.fails

        remaining_fails = await semi_mocked_function_with_some_retries(FailsBeforeSuccess(8))
        self.assertEqual(remaining_fails, 0)

    @tornado.testing.gen_test
    async def test_raises_runtime_error_if_it_fails_more_than_the_configured_retries_async(self):
        job = FakeTestJob(self.workspace)
        job.save()

        @retry_transaction_in_case_of_concurrent_edition_error_async(tries=3, delay=0.001, backoff=1)
        async def semi_mocked_function_with_some_retries(job, fail_before_success):
            with Job.transaction(job.id) as j:
                if fail_before_success.fails != 0:
                    print(fail_before_success.fails)
                    fail_before_success.fails -= 1
                    j.save()
            return fail_before_success.fails

        with self.assertRaises(ConcurrentEditionException):
            await semi_mocked_function_with_some_retries(job, FailsBeforeSuccess(5))


class ParentClass(RedisModel):
    __namespace__ = 'parentclass'

    __props__ = [
        'id',
        'name'
    ]

    def __init__(self, **config):
        self.id = None
        self.name = None

        super().__init__(**config)


class ChildClass(RedisModel):
    __namespace__ = 'childclass'
    __owner__ = 'parent_id'

    __props__ = [
        'id',
        'name',
        'parent_id'
    ]

    def __init__(self, **config):
        self.id = None
        self.name = None
        self.parent_id = None

        super().__init__(**config)


class ChildClassOwnerLimited(ChildClass):
    __owner_max_children__ = 100


class TestModelOwnership(unittest.TestCase):
    def setUp(self):
        super().setUp()
        redis_client = get_redis_test_client()
        ParentClass.config(redis_client)
        ChildClass.config(redis_client)
        ChildClassOwnerLimited.config(redis_client)

    def create_parent(self, name):
        uid = str(uuid.uuid4())
        config = {
            'id': uid,
            'name': name
        }

        parent = ParentClass(**config)
        parent.save()
        return parent

    def create_child(self, parent_id, name, child_cls=ChildClass):
        uid = str(uuid.uuid4())
        config = {
            'id': uid,
            'parent_id': parent_id,
            'name': name
        }

        child = child_cls(**config)
        child.save()
        return child

    def test_simple_ownership(self):
        parent = self.create_parent('parent')
        child = self.create_child(parent.id, 'child_1')
        self.assertTrue(ChildClass.is_owned_by(child.id, parent.id))

    def test_model_with_owner_is_deleted_when_the_owner_is_deleted(self):
        parent = self.create_parent('parent')
        child = self.create_child(parent.id, 'child_1')

        children = ChildClass.get_all_by_owner(parent.id)

        self.assertEqual(children[0].id, child.id)

        ChildClass._delete(child.id)
        children = ChildClass.get_all_by_owner(parent.id)

        self.assertEqual(len(children), 0)

    @patch('random.randint', lambda a, b: RedisModel.OWNER_SET_REMOVE_EVERY_X_ADD)
    def test_get_all_by_owner_lazy_deletion_not_removing_by_default(self):
        redis_client = get_redis_test_client()

        parent = self.create_parent('parent')
        parent_owner_key = f"{ChildClass.__namespace__}:owner:{parent.id}"

        HOW_MANY_CHILDREN = 125

        def child_name(i):
            return f"child_{i}"

        for i in range(HOW_MANY_CHILDREN):
            self.create_child(parent.id, child_name(i))

        HOW_MANY_REQUESTED = 20

        # without any other action
        # we have as many children in the set as we created
        # even if the probabilistic deletion matches
        children_count = redis_client.zcard(parent_owner_key)
        self.assertEqual(children_count, HOW_MANY_CHILDREN)

        # We should return up to the limit
        children = ChildClass.get_all_by_owner(parent.id, limit=HOW_MANY_REQUESTED)
        self.assertEqual(len(children), HOW_MANY_REQUESTED)
        for i in range(HOW_MANY_REQUESTED):
            self.assertEqual(children[i].name, child_name(HOW_MANY_CHILDREN - i - 1))

        # But we should not remove anything from the set
        children_count = redis_client.zcard(parent_owner_key)
        self.assertEqual(children_count, HOW_MANY_CHILDREN)

        # We should keep them sorted by last creation
        children = ChildClass.get_all_by_owner(parent.id, limit=HOW_MANY_CHILDREN)
        for i in range(HOW_MANY_CHILDREN):
            self.assertEqual(children[i].name, child_name(HOW_MANY_CHILDREN - i - 1))

    @patch('random.randint', lambda a, b: 1)
    def test_get_all_by_owner_lazy_deletion(self):
        redis_client = get_redis_test_client()

        parent = self.create_parent('parent')
        parent_owner_key = f"{ChildClassOwnerLimited.__namespace__}:owner:{parent.id}"

        HOW_MANY_CHILDREN = 125

        def child_name(i):
            return f"child_{i}"

        for i in range(HOW_MANY_CHILDREN):
            self.create_child(parent.id, child_name(i), child_cls=ChildClassOwnerLimited)

        # without any other action and the probabilistic deletion,
        # we have as many children in the set as we created
        children_count = redis_client.zcard(parent_owner_key)
        self.assertEqual(children_count, HOW_MANY_CHILDREN)

        # We should not return more children than the limit
        children = ChildClassOwnerLimited.get_all_by_owner(parent.id, limit=HOW_MANY_CHILDREN)
        self.assertEqual(len(children), ChildClassOwnerLimited.__owner_max_children__)

        # We should have lazily deleted all but 100 children which is the limit
        children_count = redis_client.zcard(parent_owner_key)
        self.assertEqual(children_count, ChildClassOwnerLimited.__owner_max_children__)

        # We should also keep the most recent children
        children = ChildClassOwnerLimited.get_all_by_owner(parent.id, limit=ChildClassOwnerLimited.__owner_max_children__)
        for i in range(ChildClassOwnerLimited.__owner_max_children__):
            self.assertEqual(children[i].name, child_name(HOW_MANY_CHILDREN - i - 1))

    @patch('random.randint', lambda a, b: 1)
    def test_get_all_by_owner_lazy_deletion_with_smaller_limit(self):
        redis_client = get_redis_test_client()

        parent = self.create_parent('parent')
        parent_owner_key = f"{ChildClassOwnerLimited.__namespace__}:owner:{parent.id}"

        HOW_MANY_CHILDREN = 125

        def child_name(i):
            return f"child_{i}"

        for i in range(HOW_MANY_CHILDREN):
            self.create_child(parent.id, child_name(i), child_cls=ChildClassOwnerLimited)

        HOW_MANY_REQUESTED = 20

        # without any other action we have as many children in the set as we created
        children_count = redis_client.zcard(parent_owner_key)
        self.assertEqual(children_count, HOW_MANY_CHILDREN)

        # We should return up to the limit
        children = ChildClassOwnerLimited.get_all_by_owner(parent.id, limit=HOW_MANY_REQUESTED)
        self.assertEqual(len(children), HOW_MANY_REQUESTED)
        for i in range(HOW_MANY_REQUESTED):
            self.assertEqual(children[i].name, child_name(HOW_MANY_CHILDREN - i - 1))

        # We should have lazily deleted all but 100 children which is the limit
        children_count = redis_client.zcard(parent_owner_key)
        self.assertEqual(children_count, ChildClassOwnerLimited.__owner_max_children__)

        # We should also keep the most recent children
        children = ChildClassOwnerLimited.get_all_by_owner(parent.id, limit=ChildClassOwnerLimited.__owner_max_children__)
        for i in range(ChildClassOwnerLimited.__owner_max_children__):
            self.assertEqual(children[i].name, child_name(HOW_MANY_CHILDREN - i - 1))

    @patch('random.randint', lambda a, b: RedisModel.OWNER_SET_REMOVE_EVERY_X_ADD)
    def test_get_all_by_owner_probabilistic_deletion_on_add(self):
        redis_client = get_redis_test_client()

        parent = self.create_parent('parent')
        parent_owner_key = f"{ChildClassOwnerLimited.__namespace__}:owner:{parent.id}"

        HOW_MANY_CHILDREN = 125

        def child_name(i):
            return f"child_{i}"

        for i in range(HOW_MANY_CHILDREN):
            self.create_child(parent.id, child_name(i), child_cls=ChildClassOwnerLimited)

        # The probabilistic deletion should remove any extra children
        children_count = redis_client.zcard(parent_owner_key)
        self.assertEqual(children_count, ChildClassOwnerLimited.__owner_max_children__)

        # Still, we should keep the most recent children
        children = ChildClassOwnerLimited.get_all_by_owner(parent.id, limit=ChildClassOwnerLimited.__owner_max_children__)
        for i in range(ChildClassOwnerLimited.__owner_max_children__):
            self.assertEqual(children[i].name, child_name(HOW_MANY_CHILDREN - i - 1))


@dataclass
class ModelMigrationThreadConditions:
    cv_migration: threading.Condition
    is_first_thread: bool
    cv_transaction_finish: threading.Condition
    transaction_finished: bool


class TestModelMigrationDoesNotLeaveCorruptedData(unittest.TestCase):

    stored_thread_conditions = defaultdict(lambda: ModelMigrationThreadConditions(
        cv_migration=threading.Condition(),
        is_first_thread=True,
        cv_transaction_finish=threading.Condition(),
        transaction_finished=False
    ))

    # The first time this is called it is by the "slow thread", to simulate this we wait until the main transaction is
    # done The second time this is called it is by the fast thread, where we don't wait for anything and overtake
    # the slow thread
    @staticmethod
    def migration_with_wait(u):
        print(str(threading.get_ident()) + " Started migration")

        thread_conditions = TestModelMigrationDoesNotLeaveCorruptedData.stored_thread_conditions[u['id']]
        is_first = False
        with thread_conditions.cv_migration:
            if thread_conditions.is_first_thread:
                is_first = True
                thread_conditions.is_first_thread = False
                thread_conditions.cv_migration.notify()

        if is_first:
            with thread_conditions.cv_transaction_finish:
                thread_conditions.cv_transaction_finish.wait()

        u['value_to_check'] = "value_written_in_migration"
        print(str(threading.get_ident()) + " completed migration")
        return u

    # This is a slow thread transaction
    # It is executed first so it starts the migrations, but before it is done a second thread also starts the
    # transactions and it finishes first. When the first thread finishes, as there has been a concurrent edit, it
    # will get an exception and retry to read the object; as the object has already been migrated (thread #2) it
    # doesn't need to run migrations again
    def _execute_slow_transaction(self, example_id):
        print(str(threading.get_ident()) + " Started change in SLOW thread")

        migration_id = ExampleModelForMigrationChecks.get_by_id(example_id)
        self.assertEqual(migration_id.value_to_check, 'change_in_fast_transaction')
        print(str(threading.get_ident()) + " Completed change in SLOW thread")

    def test_modifications_to_user_returned_by_get_by_id_does_not_appears_as_modified_in_other_objects(self):

        example_id = f'example_id_{uuid.uuid4().hex}'

        example = ExampleModelForMigrationChecks(id=example_id)
        example.save()

        # The migration was not executed as the object is directly inserted in the cache with the .save() and is
        # returned as it is using the get_by_id or the transaction.
        # Cleaning the cache will force the retrieval of the Redis model so the migration will be executed.
        ExampleModelForMigrationChecks.__object_cache_by_id__ = defaultdict(lambda: ModelLRUCache(128))

        parallel_exec = threading.Thread(target=self._execute_slow_transaction, args=(example_id,))
        parallel_exec.start()

        thread_conditions = TestModelMigrationDoesNotLeaveCorruptedData.stored_thread_conditions[example_id]

        # Don't do anything until the slow thread has already started doing migrations
        with thread_conditions.cv_migration:
            thread_conditions.cv_migration.wait()

        print(str(threading.get_ident()) + " Starting transaction in FAST thread")
        with ExampleModelForMigrationChecks.transaction(example_id) as example:
            example.value_to_check = "change_in_fast_transaction"

        print(str(threading.get_ident()) + " Completed change in FAST thread")
        # Notify the slow thread that the fast thread has finished so it stops waiting (simulating it's slow)
        with thread_conditions.cv_transaction_finish:
            thread_conditions.transaction_finished = True
            thread_conditions.cv_transaction_finish.notify()

        parallel_exec.join()
        example = ExampleModelForMigrationChecks.get_by_id(example_id)

        self.assertEqual(example.value_to_check, 'change_in_fast_transaction')


class ExampleModelForMigrationChecks(RedisModel):
    __namespace__ = 'examplemodel'
    __props__ = ['value_to_check']

    __migrations__ = {
        1: TestModelMigrationDoesNotLeaveCorruptedData.migration_with_wait
    }

    def __init__(self, **config):
        self.value_to_check = None
        super().__init__(**config)
