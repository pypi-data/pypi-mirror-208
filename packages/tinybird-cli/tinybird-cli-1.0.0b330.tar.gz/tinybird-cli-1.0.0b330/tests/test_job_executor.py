import unittest
import uuid
import time
import asyncio

from tinybird.redis_client import TBRedisConfig, get_redis_test_client, get_redis_config
from tinybird.job import JobExecutor, Job, JobKind, JobStatus
from tinybird.user import User, UserAccount
from tinybird.ch import HTTPClient
from .utils import get_finalised_job_async


PYTHON_THREAD_TOLERANCE_IN_SECONDS = 2


class FakeTestJob(Job):
    def __init__(self, kind, user, job_time=None):
        Job.__init__(self, kind, user)
        self.database_server = user['database_server']
        self.job_time = job_time
        self.save()

    def run(self):
        def function_to_execute(job):
            if self.job_time:
                time.sleep(self.job_time)
            job.status = JobStatus.DONE
            job.save()
            self.job_executor.job_finished(job)

        self.job_executor.submit(function_to_execute, self)


class TestJobExecutor(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        super().setUp()

        redis_config: TBRedisConfig = get_redis_config()

        self.user, self.user_account = self.new_user()

        self.client = HTTPClient(self.user.database_server, database=None)
        self.client.query_sync(f"CREATE DATABASE IF NOT EXISTS {self.user.database} ON CLUSTER tinybird", read_only=False)

        JobExecutor.CHECK_NEW_QUEUES_FREQ_IN_SECONDS = 0.05
        JobExecutor.ALIVE_QUEUES_TTL_IN_SECONDS = 1
        redis_client = get_redis_test_client()
        self.job_executor_producer = JobExecutor(redis_client=redis_client, redis_config=redis_config, consumer=False, import_workers=0, query_workers=0, export_workers=0, branching_workers=0)
        self.job_executor_consumer = JobExecutor(redis_client=redis_client, redis_config=redis_config, consumer=True, import_workers=1, query_workers=1, export_workers=1, branching_workers=1)
        self.job_consumer = self.job_executor_consumer.start_consumer()

    def tearDown(self):
        self.job_consumer.terminate()
        self.job_consumer.join()
        self.job_executor_producer.join(wait=True)
        self.job_executor_consumer.join(wait=True)
        self.job_executor_consumer._clean()

        self.delete_user(self.user, self.user_account)
        super().tearDown()

    def new_user(self):
        WORKSPACE = f'test_job_executor_{str(int(time.time()))}_{uuid.uuid4().hex}'
        USER = f'{WORKSPACE}@example.com'

        try:
            user_account = UserAccount.get_by_email(USER)
            UserAccount._delete(user_account.id)
        except Exception:
            pass

        user_account = UserAccount.register(USER, 'pass')
        user = User.register(
            name=WORKSPACE,
            admin=user_account.id
        )

        return user, user_account

    def delete_user(self, user, user_account):
        User._delete(user.id)
        UserAccount._delete(user_account.id)
        self.client.query_sync(f"DROP DATABASE IF EXISTS `{user.database}` ON CLUSTER tinybird", read_only=False)

    async def check_threadpool_exists(self, threadpool):
        start = time.time()
        while (time.time() - start) < (JobExecutor.ALIVE_QUEUES_TTL_IN_SECONDS + PYTHON_THREAD_TOLERANCE_IN_SECONDS):
            if self.user.database_server in threadpool:
                return
            await asyncio.sleep(JobExecutor.CHECK_NEW_QUEUES_FREQ_IN_SECONDS)
        self.assertTrue(False)

    async def check_discover_new_queue(self, kind):
        job = FakeTestJob(kind, self.user)
        self.job_executor_producer.put_job(job)

        if kind == JobKind.IMPORT:
            self.assertTrue(self.user.database_server in self.job_executor_producer._import_threadpool_executors)
            self.assertEqual(self.job_executor_producer._import_threadpool_executors[self.user.database_server]._thread_pool_executor, None)
            self.assertEqual(len(self.job_executor_producer._query_threadpool_executors), 0)
            self.assertEqual(len(self.job_executor_consumer._export_threadpool_executors), 0)
            self.assertEqual(len(self.job_executor_consumer._branching_threadpool_executors), 0)
            await self.check_threadpool_exists(self.job_executor_consumer._import_threadpool_executors)
            self.assertEqual(len(self.job_executor_consumer._query_threadpool_executors), 0)
            self.assertEqual(len(self.job_executor_consumer._export_threadpool_executors), 0)
            self.assertEqual(len(self.job_executor_consumer._branching_threadpool_executors), 0)
        elif kind == JobKind.COPY:
            self.assertTrue(self.user.database_server in self.job_executor_producer._export_threadpool_executors)
            self.assertEqual(self.job_executor_producer._export_threadpool_executors[self.user.database_server]._thread_pool_executor, None)
            self.assertEqual(len(self.job_executor_consumer._query_threadpool_executors), 0)
            self.assertEqual(len(self.job_executor_consumer._import_threadpool_executors), 0)
            self.assertEqual(len(self.job_executor_consumer._branching_threadpool_executors), 0)
            await self.check_threadpool_exists(self.job_executor_consumer._export_threadpool_executors)
            self.assertEqual(len(self.job_executor_consumer._query_threadpool_executors), 0)
            self.assertEqual(len(self.job_executor_consumer._import_threadpool_executors), 0)
            self.assertEqual(len(self.job_executor_consumer._branching_threadpool_executors), 0)
        elif kind == JobKind.REGRESSION:
            self.assertTrue(self.user.database_server in self.job_executor_producer._branching_threadpool_executors)
            self.assertEqual(self.job_executor_producer._branching_threadpool_executors[self.user.database_server]._thread_pool_executor, None)
            self.assertEqual(len(self.job_executor_consumer._query_threadpool_executors), 0)
            self.assertEqual(len(self.job_executor_consumer._import_threadpool_executors), 0)
            self.assertEqual(len(self.job_executor_consumer._export_threadpool_executors), 0)
            await self.check_threadpool_exists(self.job_executor_consumer._branching_threadpool_executors)
            self.assertEqual(len(self.job_executor_consumer._query_threadpool_executors), 0)
            self.assertEqual(len(self.job_executor_consumer._import_threadpool_executors), 0)
            self.assertEqual(len(self.job_executor_consumer._export_threadpool_executors), 0)
        else:
            self.assertTrue(self.user.database_server in self.job_executor_producer._query_threadpool_executors)
            self.assertEqual(self.job_executor_producer._query_threadpool_executors[self.user.database_server]._thread_pool_executor, None)
            self.assertEqual(len(self.job_executor_consumer._query_threadpool_executors), 0)
            self.assertEqual(len(self.job_executor_consumer._branching_threadpool_executors), 0)
            await self.check_threadpool_exists(self.job_executor_consumer._query_threadpool_executors)
            self.assertEqual(len(self.job_executor_consumer._import_threadpool_executors), 0)
            self.assertEqual(len(self.job_executor_consumer._export_threadpool_executors), 0)
            self.assertEqual(len(self.job_executor_consumer._branching_threadpool_executors), 0)

    async def check_threadpool_executors_is_empty(self, threadpool):
        start = time.time()
        while (time.time() - start) < (JobExecutor.ALIVE_QUEUES_TTL_IN_SECONDS + JobExecutor.CHECK_NEW_QUEUES_FREQ_IN_SECONDS + 2 * PYTHON_THREAD_TOLERANCE_IN_SECONDS):
            if len(threadpool) == 0:
                return
            await asyncio.sleep(JobExecutor.CHECK_NEW_QUEUES_FREQ_IN_SECONDS)
        self.assertTrue(False)

    async def test_discover_new_import_queue(self):
        await self.check_discover_new_queue(JobKind.IMPORT)

    async def test_discover_new_query_queue(self):
        await self.check_discover_new_queue(JobKind.POPULATE)

    async def test_discover_new_export_queue(self):
        await self.check_discover_new_queue(JobKind.COPY)

    async def test_import_workers_shutdown(self):
        await self.check_discover_new_queue(JobKind.IMPORT)
        await self.check_threadpool_executors_is_empty(self.job_executor_consumer._import_threadpool_executors)

    async def test_query_workers_shutdown(self):
        await self.check_discover_new_queue(JobKind.QUERY)
        await self.check_threadpool_executors_is_empty(self.job_executor_consumer._query_threadpool_executors)

    async def test_export_workers_shutdown(self):
        await self.check_discover_new_queue(JobKind.COPY)
        await self.check_threadpool_executors_is_empty(self.job_executor_consumer._export_threadpool_executors)

    async def test_branching_workers_shutdown(self):
        await self.check_discover_new_queue(JobKind.REGRESSION)
        await self.check_threadpool_executors_is_empty(self.job_executor_consumer._branching_threadpool_executors)

    async def test_discover_new_import_query_and_export_queue(self):
        job1 = FakeTestJob(JobKind.IMPORT, self.user)
        job2 = FakeTestJob(JobKind.DELETE_DATA, self.user)
        job3 = FakeTestJob(JobKind.COPY, self.user)
        job4 = FakeTestJob(JobKind.REGRESSION, self.user)
        self.job_executor_producer.put_job(job1)
        self.job_executor_producer.put_job(job2)
        self.job_executor_producer.put_job(job3)
        self.job_executor_producer.put_job(job4)
        self.assertTrue(self.user.database_server in self.job_executor_producer._import_threadpool_executors)
        self.assertTrue(self.user.database_server in self.job_executor_producer._query_threadpool_executors)
        self.assertTrue(self.user.database_server in self.job_executor_producer._export_threadpool_executors)
        self.assertTrue(self.user.database_server in self.job_executor_producer._branching_threadpool_executors)
        self.assertEqual(self.job_executor_producer._import_threadpool_executors[self.user.database_server]._thread_pool_executor, None)
        self.assertEqual(self.job_executor_producer._query_threadpool_executors[self.user.database_server]._thread_pool_executor, None)
        self.assertEqual(self.job_executor_producer._export_threadpool_executors[self.user.database_server]._thread_pool_executor, None)
        self.assertEqual(self.job_executor_producer._branching_threadpool_executors[self.user.database_server]._thread_pool_executor, None)
        await self.check_threadpool_exists(self.job_executor_consumer._import_threadpool_executors)
        await self.check_threadpool_exists(self.job_executor_consumer._query_threadpool_executors)
        await self.check_threadpool_exists(self.job_executor_consumer._export_threadpool_executors)
        await self.check_threadpool_exists(self.job_executor_consumer._branching_threadpool_executors)

    async def test_all_workers_shutdown(self):
        await self.test_discover_new_import_query_and_export_queue()
        await self.check_threadpool_executors_is_empty(self.job_executor_consumer._import_threadpool_executors)
        await self.check_threadpool_executors_is_empty(self.job_executor_consumer._query_threadpool_executors)
        await self.check_threadpool_executors_is_empty(self.job_executor_consumer._export_threadpool_executors)
        await self.check_threadpool_executors_is_empty(self.job_executor_consumer._branching_threadpool_executors)

    async def test_import_workers_shutdown_after_job_finishes(self):
        job = FakeTestJob(JobKind.IMPORT, self.user, JobExecutor.ALIVE_QUEUES_TTL_IN_SECONDS + PYTHON_THREAD_TOLERANCE_IN_SECONDS)
        self.job_executor_producer.put_job(job)
        await self.check_threadpool_exists(self.job_executor_consumer._import_threadpool_executors)
        await asyncio.sleep(JobExecutor.ALIVE_QUEUES_TTL_IN_SECONDS)
        self.assertTrue(self.user.database_server in self.job_executor_consumer._import_threadpool_executors)
        await self.check_threadpool_executors_is_empty(self.job_executor_consumer._import_threadpool_executors)

    async def test_query_workers_shutdown_after_job_finishes(self):
        job = FakeTestJob(JobKind.QUERY, self.user, JobExecutor.ALIVE_QUEUES_TTL_IN_SECONDS + PYTHON_THREAD_TOLERANCE_IN_SECONDS)
        self.job_executor_producer.put_job(job)
        await self.check_threadpool_exists(self.job_executor_consumer._query_threadpool_executors)
        await asyncio.sleep(JobExecutor.ALIVE_QUEUES_TTL_IN_SECONDS)
        self.assertTrue(self.user.database_server in self.job_executor_consumer._query_threadpool_executors)
        await self.check_threadpool_executors_is_empty(self.job_executor_consumer._query_threadpool_executors)

    async def test_export_workers_shutdown_after_job_finishes(self):
        job = FakeTestJob(JobKind.COPY, self.user, JobExecutor.ALIVE_QUEUES_TTL_IN_SECONDS + PYTHON_THREAD_TOLERANCE_IN_SECONDS)
        self.job_executor_producer.put_job(job)
        await self.check_threadpool_exists(self.job_executor_consumer._export_threadpool_executors)
        await asyncio.sleep(JobExecutor.ALIVE_QUEUES_TTL_IN_SECONDS)
        self.assertTrue(self.user.database_server in self.job_executor_consumer._export_threadpool_executors)
        await self.check_threadpool_executors_is_empty(self.job_executor_consumer._export_threadpool_executors)

    async def test_branching_workers_shutdown_after_job_finishes(self):
        job = FakeTestJob(JobKind.REGRESSION, self.user, JobExecutor.ALIVE_QUEUES_TTL_IN_SECONDS + PYTHON_THREAD_TOLERANCE_IN_SECONDS)
        self.job_executor_producer.put_job(job)
        await self.check_threadpool_exists(self.job_executor_consumer._branching_threadpool_executors)
        await asyncio.sleep(JobExecutor.ALIVE_QUEUES_TTL_IN_SECONDS)
        self.assertTrue(self.user.database_server in self.job_executor_consumer._branching_threadpool_executors)
        await self.check_threadpool_executors_is_empty(self.job_executor_consumer._branching_threadpool_executors)

    async def test_long_import_worker_and_short_one_after_that(self):
        job1 = FakeTestJob(JobKind.IMPORT, self.user, JobExecutor.ALIVE_QUEUES_TTL_IN_SECONDS)
        job2 = FakeTestJob(JobKind.IMPORT, self.user)
        self.job_executor_producer.put_job(job1)
        self.job_executor_producer.put_job(job2)
        self.assertTrue(self.user.database_server in self.job_executor_producer._import_threadpool_executors)
        self.assertEqual(len(self.job_executor_producer._query_threadpool_executors), 0)
        self.assertEqual(self.job_executor_producer._import_threadpool_executors[self.user.database_server]._thread_pool_executor, None)
        await self.check_threadpool_exists(self.job_executor_consumer._import_threadpool_executors)
        await get_finalised_job_async(job1.id)
        await get_finalised_job_async(job2.id)
        await self.check_threadpool_exists(self.job_executor_consumer._import_threadpool_executors)
        await self.check_threadpool_executors_is_empty(self.job_executor_consumer._query_threadpool_executors)
