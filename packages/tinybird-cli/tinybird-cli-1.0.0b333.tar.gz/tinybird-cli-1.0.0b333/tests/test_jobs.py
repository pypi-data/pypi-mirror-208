from multiprocessing import Manager
import unittest
from time import time
from typing import Set, Callable
import uuid

from tinybird.ch import ch_create_materialized_view_sync, HTTPClient
from tinybird.ch_utils.engine import engine_local_to_replicated
from tinybird.job import Job, JobStatus, new_populate_job, PopulateJob, JobCancelledException, JobExecutor
from tinybird.user import User, UserAccount
from tinybird.redis_client import get_redis_test_client, get_redis_config

from tests.conftest import DEFAULT_CLUSTER
from .utils import get_finalised_job_async, exec_sql, wait_until_job_is_in_expected_status_async

# Global Manager to handle locks across different instances of the same Job,
# potentially from different threads. This is used instead of `threading.Event`
# because it can be serialized/deserialized into/from Redis without problems.
# This way, both the `FakeTestJob` and the deserialized jobs collected using
# `Job.get_by_id` share the same lock and can be synchronized.
global_lock_manager = Manager()


class ExitJobWithoutMarkingItAsDone(Exception):
    pass


class FakeTestJob(Job):

    def __init__(self, user, cancellable_status: Set[JobStatus] = None, block_job_before_executing_it=False):
        self.user = user  # workspace FIXME?
        self.database_server = user['database_server']
        self.database = user['database']
        self.internal_result = None

        self._cancellable_status = cancellable_status

        # Set of events used to block the job in different statuses so it's easier to test things
        self.before_execution_event = global_lock_manager.Event()
        self.block_job_before_executing_it = block_job_before_executing_it
        self.job_already_blocked_before_execution = global_lock_manager.Event()

        self.exit_event = global_lock_manager.Event()

        # Event to wait until a JOB is finished, either as DONE, ERROR or CANCELLED
        self.mark_as_finalised_event = global_lock_manager.Event()
        self.mark_as_working_event = global_lock_manager.Event()

        self.exit_from_block_before_execution = False
        self.do_not_submit = False

        Job.__init__(self, "test", user)

    def mark_as_done(self, result, stats):
        super().mark_as_done(result, stats)
        self.mark_as_finalised_event.set()

    def mark_as_error(self, result):
        super().mark_as_error(result)
        self.mark_as_finalised_event.set()

    def mark_as_cancelled(self):
        super().mark_as_cancelled()
        self.mark_as_finalised_event.set()

    def mark_as_working(self):
        super().mark_as_working()
        self.mark_as_working_event.set()

    def wait_until_finalised(self):
        self.mark_as_finalised_event.wait()
        return Job.get_by_id(self.id)

    def wait_until_working(self):
        self.mark_as_working_event.wait()
        return Job.get_by_id(self.id)

    def to_json(self, u=None, debug=None):
        d = {
            "id": self.id,
            "status": self.status
        }
        return d

    def finish(self, result=None):
        self.internal_result = result
        self.save()
        self.exit_event.set()

    def run(self):
        def done(f):
            try:
                result = f.result()
            except JobCancelledException:
                self.mark_as_cancelled()
            except ExitJobWithoutMarkingItAsDone:
                return
            except Exception as e:
                try:
                    self.mark_as_error({'error': str(e)})
                except Exception:
                    pass
            else:
                self.mark_as_done(result, None)

        def function():
            def _wrapper(job):
                return FakeTestJob.run_until_event(job)
            return _wrapper

        if not self.do_not_submit:
            future = self.job_executor.submit(function_to_execute=function(), job=self)
            future.add_done_callback(done)
        return self

    @staticmethod
    def run_until_event(j):
        j = Job.get_by_id(j.id)
        if j.block_job_before_executing_it:
            if j.exit_from_block_before_execution:
                raise ExitJobWithoutMarkingItAsDone()
            j.job_already_blocked_before_execution.set()
            j.before_execution_event.wait()

        j.mark_as_working()

        j.exit_event.wait()
        j = Job.get_by_id(j.id)
        if j.status == JobStatus.CANCELLING:
            raise JobCancelledException()

        if isinstance(j.internal_result, Exception):
            raise j.internal_result
        return j.internal_result

    @property
    def is_cancellable(self) -> bool:
        if self._cancellable_status is None:
            return super(FakeTestJob, self).is_cancellable
        return self.status in self._cancellable_status

    def notify_cancelled_event(self):
        self.exit_event.set()

    def set_do_not_submit(self):
        self.do_not_submit = True
        self.save()


class FailOnRunFakeJob(FakeTestJob):
    def run(self):
        raise RuntimeError('Failing before going into executor')


class BaseTestJobs(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.job_executor = JobExecutor(redis_client=get_redis_test_client(), redis_config=get_redis_config(), consumer=True, import_workers=1, query_workers=1)

    def tearDown(self):
        self.job_executor.join(wait=True)
        self.job_executor._clean()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        WORKSPACE = f'test_jobs{str(int(time()))}_{uuid.uuid4().hex}'
        USER = f'{WORKSPACE}@example.com'
        cls.user_account = UserAccount.register(USER, 'pass')

        cls.cluster_clause = "ON CLUSTER tinybird"
        cls.cluster = DEFAULT_CLUSTER

        cls.user = User.register(
            name=WORKSPACE,
            admin=cls.user_account.id,
            cluster=cls.cluster
        )

        client = HTTPClient(cls.user.database_server, database=None)
        client.query_sync(f"CREATE DATABASE IF NOT EXISTS {cls.user.database} {cls.cluster_clause}", read_only=False)

    @classmethod
    def tearDownClass(cls):
        database = cls.user.database
        client = HTTPClient(cls.user.database_server, database=cls.user.database)
        User._delete(cls.user.id)
        UserAccount._delete(cls.user_account.id)
        client.query_sync(f"DROP DATABASE IF EXISTS `{database}` {cls.cluster_clause}", read_only=False)
        super().tearDownClass()


class TestJobsCorruption(BaseTestJobs):

    def setUp(self):
        super().setUp()
        self.job_consumer = self.job_executor.start_consumer()

    def tearDown(self):
        self.job_consumer.terminate()
        self.job_consumer.join()
        super().tearDown()

    def test_happy_case(self):
        j = FakeTestJob(self.user)
        j.save()

        self.assertEqual(j.status, 'waiting')
        self.job_executor.put_job(j)

        j.finish({'task': 'ok'})

        job = j.wait_until_finalised()
        self.assertEqual(job.status, 'done')
        self.assertEqual(job.result['task'], 'ok')

    def test_happy_case_exception(self):
        j = FakeTestJob(self.user)
        j.save()

        self.assertEqual(j.status, 'waiting')
        self.job_executor.put_job(j)

        j.finish(ValueError('broken job'))

        job = j.wait_until_finalised()
        self.assertEqual(job.status, 'error')
        self.assertEqual(job.result['error'], 'broken job')

    async def test_after_populate_failure(self):
        j = await new_populate_job(self.job_executor, self.user, 'will_crash', 'select 1', 'will_crash', 'id', 'name', unlink_on_populate_error=False)

        job = await get_finalised_job_async(j.id)
        self.assertEqual(job.status, 'error')
        self.assertEqual(job.datasource, None)
        self.assertEqual(job.result['error'], "Could not find target table 'will_crash'")

        another_job = FakeTestJob(self.user)
        another_job.save()
        self.job_executor.put_job(another_job)

        another_job.finish({'task': 'ok'})
        job = another_job.wait_until_finalised()
        self.assertEqual(job.status, 'done')
        self.assertEqual(job.result['task'], 'ok')

    def test_job_failure_before_executor(self):
        j = FailOnRunFakeJob(self.user)
        j.save()

        self.assertEqual(j.status, 'waiting')
        self.job_executor.put_job(j)

        job = j.wait_until_finalised()
        self.assertEqual(job.status, 'error')
        self.assertEqual(job.result['error'], 'Job failed to finish for an unknown reason. Try again.')


class TestJobsPopulatePartitions(BaseTestJobs):

    async def _test_by_partition_populate(self, partition_key_source='', partition_key_target=''):
        extra_params = {'output_format_json_quote_64bit_integers': 0}
        cluster_clause = f"ON CLUSTER {self.user.cluster}" if self.user.cluster else ""

        id = uuid.uuid4().hex
        table_source = f'test_by_partition_populate_source_{id}'
        table_target = f'test_by_partition_populate_target_{id}'
        view_node_id = f'test_by_partition_populate_mv_{id}'

        self.user.drop_datasource(table_source)
        self.user.drop_datasource(table_target)
        table_source_ds = self.user.add_datasource(table_source)
        table_target_ds = self.user.add_datasource(table_target)

        table_source_id = table_source_ds.id
        table_target_id = table_target_ds.id

        tables = [table_source_id, table_target_id, view_node_id]
        for t in tables:
            exec_sql(self.user.database, f"DROP TABLE IF EXISTS {t} {cluster_clause}")

        engine = f"MergeTree() {partition_key_source} ORDER BY tuple()"
        if self.user.cluster:
            engine = engine_local_to_replicated(engine, self.user['database'], table_source_id)
        exec_sql(self.user.database, f"CREATE TABLE {table_source_id} {cluster_clause} (ts DateTime('UTC'), n Int32) Engine = {engine}")

        engine = f"SummingMergeTree() {partition_key_target} ORDER BY d"
        if self.user.cluster:
            engine = engine_local_to_replicated(engine, self.user['database'], table_target_id)
        exec_sql(self.user.database, f"CREATE TABLE {table_target_id} {cluster_clause} (d Date, n Int32) Engine = {engine}")

        # Only odd hours of odd days of the month:
        # - 1st of January has 12 hours with data
        # - 4th of February has 0 hours with data
        exec_sql(self.user.database, f"INSERT INTO {table_source_id} SELECT toDateTime('2021-01-01 00:00:00', 'UTC') + toIntervalHour(number) AS ts, number % 2 * toDayOfMonth(toDate(ts)) % 2 AS n FROM numbers(105 * 24)")

        def check_result(result):
            self.assertEqual(result[0], {'d': '2021-01-01', 'n': 12})
            self.assertEqual(result[1], {'d': '2021-01-02', 'n': 0})
            self.assertEqual(result[31 + 28 - 1], {'d': '2021-02-28', 'n': 0})
            self.assertEqual(result[31 + 28 + 1 - 1], {'d': '2021-03-01', 'n': 12})
            self.assertEqual(result[-2], {'d': '2021-04-14', 'n': 0})
            self.assertEqual(result[-1], {'d': '2021-04-15', 'n': 12})

        # Once the materialization is done only dates with data are kept
        def check_final_result(result):
            self.assertEqual(len(result), 54)
            self.assertEqual(result[0], {'d': '2021-01-01', 'n': 12})
            self.assertEqual(result[1], {'d': '2021-01-03', 'n': 12})
            self.assertEqual(result[-2], {'d': '2021-04-13', 'n': 12})
            self.assertEqual(result[-1], {'d': '2021-04-15', 'n': 12})

        source_result = exec_sql(self.user.database, f"""
            SELECT
                toDate(ts) d,
                sum(n) as n
            FROM {self.user.database}.{table_source_id}
            GROUP BY d
            ORDER BY d ASC
            FORMAT JSON""", extra_params)['data']

        check_result(source_result)

        view_sql = f"""
            SELECT
                toDate(ts) d,
                sum(n) as n
            FROM {self.user.database}.{table_source_id}
            GROUP BY d
        """
        ch_create_materialized_view_sync(
            self.user.database_server,
            self.user.database,
            view_name=view_node_id,
            sql=view_sql,
            target_table=table_target_id,
            cluster=self.user.cluster
        )
        j = PopulateJob(user=self.user, view_node=view_node_id, view_sql=view_sql, target_table=table_target_id)
        self.job_executor.put_job(j)
        j.save()
        j.run()

        job = await get_finalised_job_async(j.id)

        self.assertEqual(job.status, JobStatus.DONE, job.result)

        # Use FINAL here to ensure we get final results
        target_result = exec_sql(self.user.database, f"""
            SELECT * FROM {table_target_id} FINAL
            ORDER BY d ASC
            FORMAT JSON
        """, extra_params)['data']
        check_final_result(target_result)

    async def test_by_partition_populate_no_partition(self):
        await self._test_by_partition_populate()

    async def test_by_partition_populate_yyyymm_partition(self):
        await self._test_by_partition_populate(partition_key_source='PARTITION BY toYYYYMM(ts)', partition_key_target='PARTITION BY toYYYYMM(d)')


class TestPopulateCancellationFunction(BaseTestJobs):

    def test_returns_false_if_job_not_in_cancelling(self):
        j = PopulateJob(user=self.user, view_node=None, view_sql=None, target_table=None)
        j.save()

        has_been_cancelled_function = j.has_been_externally_cancelled_function_generator()
        self.assertFalse(has_been_cancelled_function())

    def test_returns_true_if_job_in_cancelling(self):
        j = PopulateJob(user=self.user, view_node=None, view_sql=None, target_table=None)
        j.status = JobStatus.CANCELLING
        j.save()

        has_been_cancelled_function = j.has_been_externally_cancelled_function_generator()
        self.assertTrue(has_been_cancelled_function())

    def test_with_the_function_detect_that_a_job_gets_cancelled(self):
        j = PopulateJob(user=self.user, view_node=None, view_sql=None, target_table=None)
        j.save()

        has_been_cancelled_function = j.has_been_externally_cancelled_function_generator()
        self.assertFalse(has_been_cancelled_function())

        j.status = JobStatus.CANCELLING
        j.save()
        self.assertTrue(has_been_cancelled_function())


class ChecksUntilCancellation:
    def __init__(self, checks_remaining):
        self.calls_done = 0
        self.checks_remaining = checks_remaining


class PopulateJobWithCustomCancellable(PopulateJob):

    def __init__(self, user, view_node, view_sql, target_table, checks_until_cancellation):
        self.checks_until_cancellation = checks_until_cancellation
        super().__init__(user, view_node=view_node, view_sql=view_sql, target_table=target_table)

    def has_been_externally_cancelled_function_generator(self) -> Callable[[], bool]:

        def has_been_cancelled() -> bool:
            self.checks_until_cancellation.calls_done += 1

            if self.checks_until_cancellation.checks_remaining == 0:
                self.try_to_cancel()
                self.checks_until_cancellation.checks_remaining -= 1
                return True
            elif self.checks_until_cancellation.checks_remaining < 0:
                return True
            else:
                self.checks_until_cancellation.checks_remaining -= 1
                return False

        return has_been_cancelled


class TestJobsPopulateCancellations(BaseTestJobs):

    async def _create_custom_populate_and_return_it_finished(self, checks_until_cancellation):
        cluster_clause = f"ON CLUSTER {self.user.cluster}" if self.user.cluster else ""
        id = uuid.uuid4().hex
        table_source = f'cancel_test_by_partition_populate_source{id}'
        table_target = f'cancel_test_by_partition_populate_target{id}'
        view_node_id = f'cancel_test_by_partition_populate_mv{id}'

        self.user.drop_datasource(table_source)
        self.user.drop_datasource(table_target)
        table_source_ds = self.user.add_datasource(table_source)
        table_target_ds = self.user.add_datasource(table_target)

        table_source_id = table_source_ds.id
        table_target_id = table_target_ds.id

        tables = [table_source_id, table_target_id, view_node_id]

        tables = [table_source_id, table_target_id, view_node_id]
        for t in tables:
            exec_sql(self.user.database, f"DROP TABLE IF EXISTS {t} {cluster_clause}")

        engine = "MergeTree() PARTITION BY toYYYYMM(ts, 'UTC') ORDER BY tuple()"
        if self.user.cluster:
            engine = engine_local_to_replicated(engine, self.user['database'], table_source_id)
        exec_sql(self.user.database, f"CREATE TABLE {table_source_id} {cluster_clause} (ts DateTime('UTC'), n Int32) Engine = {engine}")

        engine = "SummingMergeTree() PARTITION BY toYYYYMM(d, 'UTC') ORDER BY d"
        if self.user.cluster:
            engine = engine_local_to_replicated(engine, self.user['database'], table_target_id)
        exec_sql(self.user.database, f"CREATE TABLE {table_target_id} {cluster_clause} (d Date, n Int32) Engine = {engine}")

        # Only odd hours of odd days of the month:
        # - 1st of January has 12 hours with data
        # - 4th of February has 0 hours with data
        exec_sql(self.user.database,
                 f"INSERT INTO {table_source_id} SELECT toDateTime('2021-01-01 00:00:00', 'UTC') + toIntervalHour(number) AS ts, number % 2 * toDayOfMonth(toDate(ts)) % 2 AS n FROM numbers(105 * 24)")

        view_sql = f"""
                    SELECT
                        toDate(ts, 'UTC') d,
                        sum(n) as n
                    FROM
                        {self.user.database}.{table_source_id},
                        (SELECT max(number) as number FROM (SELECT number from system.numbers LIMIT 100000000)) as t
                    GROUP BY d
                """
        ch_create_materialized_view_sync(
            self.user.database_server,
            self.user.database,
            view_name=view_node_id,
            sql=view_sql,
            target_table=table_target_id,
            cluster=self.user.cluster
        )
        j = PopulateJobWithCustomCancellable(
            user=self.user, view_node=view_node_id, view_sql=view_sql,
            target_table=table_target_id, checks_until_cancellation=checks_until_cancellation)
        self.job_executor.put_job(j)
        j.save()
        j.run()

        return await wait_until_job_is_in_expected_status_async(j.id, [JobStatus.CANCELLED], max_retries=400)

    async def test_populate_cancellation_may_be_cancelled_inmediately_without_executing_the_queries(self):
        checks_until_cancellation = ChecksUntilCancellation(0)

        job = await self._create_custom_populate_and_return_it_finished(checks_until_cancellation)

        self.assertEqual(job.status, JobStatus.CANCELLED, job.result)
        self.assertEqual(checks_until_cancellation.calls_done, 5)
        queries_cancelled = len(list(filter(lambda query: query.status == 'cancelled', job.queries)))
        self.assertEqual(queries_cancelled, 4)

    async def test_populate_cancellation_may_be_cancelled_and_leave_some_queries_cancelled_and_other_done(self):
        checks_until_cancellation = ChecksUntilCancellation(10)

        job = await self._create_custom_populate_and_return_it_finished(checks_until_cancellation)

        self.assertEqual(job.status, JobStatus.CANCELLED, job.result)
        # It's difficult to get exacts numbers without mocking the checks as it depends on the communication between
        # the backend and CH
        self.assertGreaterEqual(checks_until_cancellation.calls_done, 10)
        self.assertLess(checks_until_cancellation.calls_done, 20)
        queries_cancelled = len(list(filter(lambda query: query.status == 'cancelled', job.queries)))
        self.assertGreaterEqual(queries_cancelled, 1)
        self.assertLess(queries_cancelled, 4)


class TestJobCancellation(BaseTestJobs):
    def setUp(self):
        super().setUp()
        self.job_consumer = self.job_executor.start_consumer()

    def tearDown(self):
        self.job_consumer.terminate()
        self.job_consumer.join()
        super().tearDown()

    def test_job_correctly_set_as_cancelled_from_waiting_status(self):
        j = FakeTestJob(self.user, cancellable_status={JobStatus.WAITING}, block_job_before_executing_it=True)
        j.save()
        self.assertEqual(len(self.job_executor.get_pending_jobs()), 0)
        self.job_executor.put_job(j)

        j.job_already_blocked_before_execution.wait()

        j = Job.get_by_id(j.id)
        self.assertEqual(JobStatus.WAITING, j.status)

        pending_job_ids = [job.id for job in self.job_executor.get_pending_jobs()]
        self.assertIn(j.id, pending_job_ids)

        j.try_to_cancel()
        j = Job.get_by_id(j.id)
        self.assertEqual(JobStatus.CANCELLED, j.status)

        self.assertEqual(len(self.job_executor.get_pending_jobs()), 0)
        j.before_execution_event.set()  # Unblock the blocked job

    def test_job_correctly_set_as_cancelled_from_cancelling_status(self):
        j = FakeTestJob(self.user, cancellable_status={JobStatus.WAITING, JobStatus.WORKING})
        j.save()
        self.assertEqual(len(self.job_executor.get_pending_jobs()), 0)
        self.job_executor.put_job(j)

        j = j.wait_until_working()
        j.try_to_cancel()
        j = Job.get_by_id(j.id)
        self.assertEqual(JobStatus.CANCELLING, j.status)
        pending_job_ids = [job.id for job in self.job_executor.get_pending_jobs()]
        self.assertIn(j.id, pending_job_ids)

        j.notify_cancelled_event()
        j.wait_until_finalised()

        j = Job.get_by_id(j.id)
        self.assertEqual(JobStatus.CANCELLED, j.status)
        self.assertEqual(len(self.job_executor.get_pending_jobs()), 0)


class TestJobOwnership(BaseTestJobs):

    def test_job_is_owned_by_user(self):
        j = PopulateJob(user=self.user, view_node="", view_sql="", target_table="")
        j.save()

        is_owned = Job.is_owned_by(j.id, self.user.id)
        self.assertTrue(is_owned)

    def test_job_is_not_owned_by_other_user(self):
        j = PopulateJob(user=self.user, view_node="", view_sql="", target_table="")
        j.save()

        is_owned = Job.is_owned_by(j.id, "other_user_id")
        self.assertFalse(is_owned)


class TestPendingJobs(BaseTestJobs):

    def test_job_in_pending(self):
        j = FakeTestJob(self.user)
        j.save()
        consumer = self.job_executor.start_consumer()
        try:
            self.assertEqual(j.status, JobStatus.WORKING)

            self.assertEqual(j.status, 'waiting')
            self.job_executor.put_job(j)

            j = j.wait_until_working()

            pending_job_ids = [job.id for job in self.job_executor.get_pending_jobs()]
            self.assertIn(j.id, pending_job_ids)

            j.finish({'task': 'ok'})

            job = j.wait_until_finalised()
            self.assertEqual(job.status, 'done')
            self.assertEqual(job.result['task'], 'ok')

            pending_job_ids = [job.id for job in self.job_executor.get_pending_jobs()]
            self.assertNotIn(j.id, pending_job_ids)
        except Exception:
            consumer.terminate()
            consumer.join()

    def test_pending_and_wip_and_queued_jobs(self):
        j = FakeTestJob(self.user)
        j.set_do_not_submit()
        j.save()

        self.assertEqual(j.status, 'waiting')
        self.job_executor.put_job(j)

        wip_jobs, queued_jobs = self.job_executor.get_wip_and_queued_jobs()
        pending_jobs = self.job_executor.get_pending_jobs()

        self.assertEqual(pending_jobs, wip_jobs + queued_jobs)

    def _common_pending_test(self, status, in_pending=True):
        j = FakeTestJob(self.user)
        j.set_do_not_submit()
        j.save()

        self.assertEqual(j.status, 'waiting')
        self.job_executor.put_job(j)

        wip_jobs = []
        queued_jobs = []
        pending_jobs = []

        def _update_pending_jobs():
            nonlocal wip_jobs, queued_jobs, pending_jobs
            wip_jobs, queued_jobs = self.job_executor.get_wip_and_queued_jobs()
            pending_jobs = self.job_executor.get_pending_jobs()
            self.assertEqual(pending_jobs, wip_jobs + queued_jobs)
            wip_jobs = [job.id for job in wip_jobs]
            queued_jobs = [job.id for job in queued_jobs]
            pending_jobs = [job.id for job in pending_jobs]

        _update_pending_jobs()
        self.assertNotIn(j.id, wip_jobs)
        self.assertIn(j.id, queued_jobs)
        self.assertIn(j.id, pending_jobs)

        j.status = status
        j.save()
        self.assertEqual(j.status, status)

        _update_pending_jobs()
        # Jobs in working status that have not been picked up to be run yet (and
        # thus, added to the WIP queue) shouldn't be present as a pending job.
        if in_pending and j.status != JobStatus.WORKING:
            self.assertNotIn(j.id, wip_jobs)
            self.assertIn(j.id, queued_jobs)
            self.assertIn(j.id, pending_jobs)
        else:
            self.assertNotIn(j.id, wip_jobs)
            self.assertNotIn(j.id, queued_jobs)
            self.assertNotIn(j.id, pending_jobs)

        # Take out of the Redis queue the job
        executors = self.job_executor.get_all_executors()
        self.assertEqual(len(executors), 1)
        job_id = executors[0].get_job()
        self.assertEqual(job_id, j.id)

        _update_pending_jobs()
        if in_pending:
            self.assertIn(j.id, wip_jobs)
            self.assertNotIn(j.id, queued_jobs)
            self.assertIn(j.id, pending_jobs)
        else:
            self.assertNotIn(j.id, wip_jobs)
            self.assertNotIn(j.id, queued_jobs)
            self.assertNotIn(j.id, pending_jobs)

    def test_waiting_job_in_pending(self):
        self._common_pending_test(JobStatus.WAITING, in_pending=True)

    def test_cancelling_job_in_pending(self):
        self._common_pending_test(JobStatus.CANCELLING, in_pending=True)

    def test_working_job_in_pending(self):
        self._common_pending_test(JobStatus.WORKING, in_pending=True)

    def test_finished_job_not_in_pending(self):
        self._common_pending_test(JobStatus.DONE, in_pending=False)

    def test_cancelled_job_not_in_pending(self):
        self._common_pending_test(JobStatus.CANCELLED, in_pending=False)

    def test_errored_job_not_in_pending(self):
        self._common_pending_test(JobStatus.ERROR, in_pending=False)

    def test_removed_job_not_in_pending(self):
        j1 = FakeTestJob(self.user)
        j1.set_do_not_submit()
        j2 = FakeTestJob(self.user)
        j2.set_do_not_submit()
        j3 = FakeTestJob(self.user)
        j3.set_do_not_submit()

        self.job_executor.put_job(j1)
        self.job_executor.put_job(j2)
        self.job_executor.put_job(j3)
        pending_job_ids = [job.id for job in self.job_executor.get_pending_jobs()]
        self.assertIn(j1.id, pending_job_ids)
        self.assertIn(j2.id, pending_job_ids)
        self.assertIn(j3.id, pending_job_ids)

        # Remove the job j2 from Redis to check that it's no longer collected as a pending job
        Job._delete(j2.id)

        # Take out of the queued all jobs so that they're added into the WIP set
        for executor in self.job_executor.get_all_executors():
            # Note that since they share the same user, they share the same database server and all 3 jobs fall
            # into the same executor, so ask it 3 times to get jobs
            _ = executor.get_job()
            _ = executor.get_job()
            _ = executor.get_job()

        pending_job_ids = [job.id for job in self.job_executor.get_pending_jobs()]
        self.assertIn(j1.id, pending_job_ids)
        self.assertNotIn(j2.id, pending_job_ids)
        self.assertIn(j3.id, pending_job_ids)
