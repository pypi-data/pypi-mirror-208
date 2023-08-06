import uuid
import pytest
from datetime import datetime, timedelta, date
from urllib.parse import urlencode
from tests.views.base_test import STRIPE_SUBSCRIPTION_MOCK, BaseTest, TBApiProxy, UsageMetricsTestMixin
from unittest.mock import patch, call, AsyncMock

from tinybird.plans import PlansService, DEFAULT_PLAN_CONFIG, PlanConfigConcepts, BuildPlanTracker
from tinybird.token_scope import scopes
from tinybird.user import User, UserAccount, public
from tinybird.constants import BillingPlans
from tinybird.views.mailgun import MailgunService, NotificationResponse
from tests.utils import exec_sql

from .conftest import is_main_process


STORAGE_BYTES = int(10.5 * (1000 ** 3))
READ_BYTES_TODAY = int(10 * (1000 ** 3))
WRITTEN_BYTES_TODAY = int(10.5 * (1000 ** 3))
READ_BYTES_YESTERDAY = int(20 * (1000 ** 3))
WRITTEN_BYTES_YESTERDAY = int(20.5 * (1000 ** 3))


STRIPE_SUBSCRIPTIONS_MOCK = {'data': [STRIPE_SUBSCRIPTION_MOCK], "has_more": False}


class TestTrackUsageRecords(BaseTest, UsageMetricsTestMixin):

    def setUp(self):
        super(TestTrackUsageRecords, self).setUp()
        self.subscriptions_to_delete = []
        self.token = UserAccount.get_by_id(self.USER_ID).get_token_for_scope(scopes.AUTH)
        self.processed_item_id = STRIPE_SUBSCRIPTION_MOCK['items']['data'][0]['id']
        self.storage_item_id = STRIPE_SUBSCRIPTION_MOCK['items']['data'][1]['id']
        self.tb_api = TBApiProxy(self)
        self.now = datetime.utcnow()
        self.today = self.now.date()
        self.yesterday = self.today - timedelta(days=1)

    def assert_usage_records(self, processed_quantity_today, storage_quantity, stripe_create_usage_record_mock,
                             timestamp_today=None,
                             timestamp_yesterday=None,
                             processed_quantity_yesterday=None):
        assert stripe_create_usage_record_mock.call_count == 2 if processed_quantity_yesterday is None else 3
        if timestamp_today is None:
            timestamp_today = datetime.combine(self.today, datetime.min.time())

        if timestamp_yesterday is None:
            timestamp_yesterday = datetime.combine(self.today, datetime.min.time()) - timedelta(days=1)

        create_usage_calls_calls = [call(id=self.processed_item_id,
                                         action='set', timestamp=timestamp_today,
                                         quantity=processed_quantity_today),
                                    call(id=self.storage_item_id,
                                         action='set', timestamp=timestamp_today,
                                         quantity=storage_quantity)]
        if processed_quantity_yesterday:
            create_usage_calls_calls.append(call(id=self.processed_item_id,
                                                 action='set', timestamp=timestamp_yesterday,
                                                 quantity=processed_quantity_yesterday))

        stripe_create_usage_record_mock.assert_has_calls(create_usage_calls_calls, any_order=True)

    @patch('stripe.SubscriptionItem.create_usage_record', return_value={})
    def test_track_usage_records_subscription_from_yesterday(
            self,
            stripe_create_usage_record_mock,
    ):
        ws_name = f'workspace_track_{uuid.uuid4().hex}'
        workspace = self.tb_api.create_workspace(self.token, ws_name)
        workspace = User.get_by_id(workspace['id'])
        self.workspaces_to_delete.append(workspace)

        self.insert_row_storage_metrics_using_usage_metrics_storage__v2(workspace,
                                                                        datetime.combine(self.today,
                                                                                         datetime.min.time()),
                                                                        10000, STORAGE_BYTES, 0, 0)
        self.insert_row_processed_metrics(workspace, self.today, READ_BYTES_TODAY,
                                          WRITTEN_BYTES_TODAY)
        self.insert_row_processed_metrics(workspace, self.yesterday, READ_BYTES_YESTERDAY,
                                          WRITTEN_BYTES_YESTERDAY)

        self.tb_api.create_customer(self.token, workspace['id'])
        self.tb_api.setup_payment_intent(self.token, workspace['id'])
        self.tb_api.subscribe_to_pro(self.token, workspace['id'])
        workspace = User.get_by_id(workspace['id'])

        subscription = STRIPE_SUBSCRIPTION_MOCK
        subscription_datetime = self.now - timedelta(days=1)
        subscription["created"] = datetime.timestamp(subscription_datetime)
        subscription["current_period_start"] = datetime.timestamp(subscription_datetime)

        metrics_cluster = "metrics"

        PlansService.track_usage_records(
            workspace,
            subscription,
            metrics_cluster)

        self.assert_usage_records(20, 10, stripe_create_usage_record_mock,
                                  processed_quantity_yesterday=40,
                                  timestamp_yesterday=subscription_datetime + timedelta(seconds=1))

    @patch('stripe.SubscriptionItem.create_usage_record', return_value={})
    def test_track_usage_records_same_day_of_subscription(
            self,
            stripe_create_usage_record_mock,
    ):
        ws_name = f'workspace_track_{uuid.uuid4().hex}'
        workspace = self.tb_api.create_workspace(self.token, ws_name)
        workspace = User.get_by_id(workspace['id'])
        self.workspaces_to_delete.append(workspace)

        self.insert_row_storage_metrics_using_usage_metrics_storage__v2(workspace,
                                                                        datetime.combine(self.today,
                                                                                         datetime.min.time()),
                                                                        10000, STORAGE_BYTES, 0, 0)
        self.insert_row_processed_metrics(workspace, self.today, READ_BYTES_TODAY,
                                          WRITTEN_BYTES_TODAY)
        self.insert_row_processed_metrics(workspace, self.yesterday, READ_BYTES_YESTERDAY,
                                          WRITTEN_BYTES_YESTERDAY)

        self.tb_api.create_customer(self.token, workspace['id'])
        self.tb_api.setup_payment_intent(self.token, workspace['id'])
        self.tb_api.subscribe_to_pro(self.token, workspace['id'])
        workspace = User.get_by_id(workspace['id'])

        subscription = STRIPE_SUBSCRIPTION_MOCK
        subscription_timestamp = self.now
        subscription["created"] = datetime.timestamp(subscription_timestamp)
        subscription["current_period_start"] = datetime.timestamp(subscription_timestamp)

        metrics_cluster = "metrics"

        PlansService.track_usage_records(
            workspace,
            subscription,
            metrics_cluster)

        self.assert_usage_records(20, 10, stripe_create_usage_record_mock,
                                  timestamp_today=subscription_timestamp + timedelta(seconds=1))

    @patch('stripe.SubscriptionItem.create_usage_record', return_value={})
    def test_track_usage_records_subscription_from_days_before(
            self,
            stripe_create_usage_record_mock,
    ):
        ws_name = f'workspace_track_{uuid.uuid4().hex}'
        workspace = self.tb_api.create_workspace(self.token, ws_name)
        workspace = User.get_by_id(workspace['id'])
        self.workspaces_to_delete.append(workspace)

        self.insert_row_storage_metrics_using_usage_metrics_storage__v2(workspace,
                                                                        datetime.combine(self.today,
                                                                                         datetime.min.time()),
                                                                        10000, STORAGE_BYTES, 0, 0)
        self.insert_row_processed_metrics(workspace, self.today, READ_BYTES_TODAY,
                                          WRITTEN_BYTES_TODAY)
        self.insert_row_processed_metrics(workspace, self.yesterday, READ_BYTES_YESTERDAY,
                                          WRITTEN_BYTES_YESTERDAY)

        self.tb_api.create_customer(self.token, workspace['id'])
        self.tb_api.setup_payment_intent(self.token, workspace['id'])
        self.tb_api.subscribe_to_pro(self.token, workspace['id'])
        workspace = User.get_by_id(workspace['id'])

        subscription = STRIPE_SUBSCRIPTION_MOCK
        subscription_datetime = self.now - timedelta(days=2)
        subscription["created"] = datetime.timestamp(subscription_datetime)
        subscription["current_period_start"] = datetime.timestamp(subscription_datetime)

        metrics_cluster = "metrics"

        PlansService.track_usage_records(
            workspace,
            subscription,
            metrics_cluster)

        self.assert_usage_records(20, 10, stripe_create_usage_record_mock,
                                  processed_quantity_yesterday=40,
                                  timestamp_yesterday=datetime.combine(self.yesterday, datetime.min.time()))

    @patch('stripe.SubscriptionItem.create_usage_record', return_value={})
    def test_track_usage_records_billing_period_starts_today(
            self,
            stripe_create_usage_record_mock,
    ):
        ws_name = f'workspace_track_{uuid.uuid4().hex}'
        workspace = self.tb_api.create_workspace(self.token, ws_name)
        workspace = User.get_by_id(workspace['id'])
        self.workspaces_to_delete.append(workspace)

        self.insert_row_storage_metrics_using_usage_metrics_storage__v2(workspace,
                                                                        datetime.combine(self.today,
                                                                                         datetime.min.time()),
                                                                        10000, STORAGE_BYTES, 0, 0)
        self.insert_row_processed_metrics(workspace, self.today, READ_BYTES_TODAY,
                                          WRITTEN_BYTES_TODAY)
        self.insert_row_processed_metrics(workspace, self.yesterday, READ_BYTES_YESTERDAY,
                                          WRITTEN_BYTES_YESTERDAY)

        self.tb_api.create_customer(self.token, workspace['id'])
        self.tb_api.setup_payment_intent(self.token, workspace['id'])
        self.tb_api.subscribe_to_pro(self.token, workspace['id'])
        workspace = User.get_by_id(workspace['id'])

        subscription = STRIPE_SUBSCRIPTION_MOCK
        subscription_datetime = self.now - timedelta(days=2)
        subscription["created"] = datetime.timestamp(subscription_datetime)
        subscription["current_period_start"] = datetime.timestamp(datetime.combine(self.today, datetime.min.time()))

        metrics_cluster = "metrics"

        PlansService.track_usage_records(
            workspace,
            subscription,
            metrics_cluster)

        self.assert_usage_records(20, 10, stripe_create_usage_record_mock,
                                  timestamp_today=datetime.fromtimestamp(subscription["current_period_start"] + 1))

    @patch('stripe.SubscriptionItem.create_usage_record', return_value={})
    def test_track_usage_records_billing_period_starts_yesterday(
            self,
            stripe_create_usage_record_mock,
    ):
        ws_name = f'workspace_track_{uuid.uuid4().hex}'
        workspace = self.tb_api.create_workspace(self.token, ws_name)
        workspace = User.get_by_id(workspace['id'])
        self.workspaces_to_delete.append(workspace)

        self.insert_row_storage_metrics_using_usage_metrics_storage__v2(workspace,
                                                                        datetime.combine(date.today(),
                                                                                         datetime.min.time()),
                                                                        10000, STORAGE_BYTES, 0, 0)
        self.insert_row_processed_metrics(workspace, self.today, READ_BYTES_TODAY,
                                          WRITTEN_BYTES_TODAY)
        self.insert_row_processed_metrics(workspace, self.yesterday, READ_BYTES_YESTERDAY,
                                          WRITTEN_BYTES_YESTERDAY)

        self.tb_api.create_customer(self.token, workspace['id'])
        self.tb_api.setup_payment_intent(self.token, workspace['id'])
        self.tb_api.subscribe_to_pro(self.token, workspace['id'])
        workspace = User.get_by_id(workspace['id'])

        subscription = STRIPE_SUBSCRIPTION_MOCK
        subscription_datetime = self.now - timedelta(days=3)
        subscription["created"] = datetime.timestamp(subscription_datetime)
        subscription["current_period_start"] = datetime.timestamp(datetime.combine(self.today,
                                                                                   datetime.min.time()) - timedelta(days=1))

        metrics_cluster = "metrics"

        PlansService.track_usage_records(
            workspace,
            subscription,
            metrics_cluster)

        self.assert_usage_records(20, 10, stripe_create_usage_record_mock,
                                  processed_quantity_yesterday=40,
                                  timestamp_yesterday=datetime.fromtimestamp(subscription["current_period_start"] + 1))


@pytest.mark.serial  # Modifies the public user
@pytest.mark.skipif(not is_main_process(), reason="Serial test")
class TestTrackBuildPlanLimits(BaseTest, UsageMetricsTestMixin):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.STORAGE_BYTES_EXCEEDED = int(11 * (1000 ** 3))
        cls.STORAGE_BYTES_REACHING = int(8 * (1000 ** 3))
        cls.STORAGE_BYTES_IN_PLAN = int(7 * (1000 ** 3))

    def tearDown(self):
        public_user = public.get_public_user()
        token = public_user.get_token_for_scope(scopes.ADMIN)
        self.tb_api.truncate_datasource(token, 'workspaces_all')
        super().tearDown()

    def setUp(self):
        super(TestTrackBuildPlanLimits, self).setUp()
        self.rand_id = f"{uuid.uuid4().hex}"
        self.user = UserAccount.register(f'test_track_build_plan_limits{self.rand_id}@example.com', 'pass')
        self.users_to_delete.append(self.user)
        self.token = self.user.get_token_for_scope(scopes.AUTH)
        self.tb_api = TBApiProxy(self)
        self.public = public.get_public_user()
        self.pipe_stats = self.public.get_datasource('pipe_stats')
        self.spans = self.public.get_datasource('spans')

    def exec_workspace_datatracker(self, workspaces):
        from tinybird.job import WorkspaceDatabaseUsageTracker
        data_tracker = WorkspaceDatabaseUsageTracker()
        data_tracker.track_model(workspaces, 'workspaces_all', ['id', 'name', 'database', 'database_server', 'plan',
                                                                'deleted', 'created_at', ('origin', lambda x: "" if x is None else x)])
        self.wait_for_public_table_replication('workspaces_all')

    def _dummy_query_api(self, token, times=1):
        params = {
            'q': 'select 1',
            'token': token
        }
        url = f'/v0/sql?{urlencode(params)}'
        for _ in range(1, times + 1):
            response = self.fetch(url)
            self.assertEqual(response.code, 200, response.body)
        self.force_flush_of_span_records()
        self.wait_for_public_table_replication('pipe_stats')

    def assertPipeStats(self, workspace, count):
        pipe_stats_result = exec_sql(self.public.database, f"select sum(view_count) as c from {self.public.database}.{self.pipe_stats.id} where user_id='{workspace.id}' AND pipe_id='query_api' FORMAT JSON")
        self.assertEqual(int(pipe_stats_result['data'][0]['c']), count, exec_sql(self.public.database, f"select * from {self.public.database}.{self.pipe_stats.id} where user_id='{workspace.id}' AND pipe_id='query_api' FORMAT JSON"))

    def assertSpans(self, workspace, count):
        pipe_stats_result = exec_sql(self.public.database, f"select count() as c from {self.public.database}.{self.spans.id} where workspace='{workspace.id}' AND operation_name = 'APIQueryHandler' FORMAT JSON")
        self.assertEqual(int(pipe_stats_result['data'][0]['c']), count, exec_sql(self.public.database, f"select * from {self.public.database}.{self.spans.id} where workspace='{workspace.id}' AND operation_name = 'APIQueryHandler' FORMAT JSON"))

    def test_track_build_plan_limits(self):
        workspace_exceeded = self.tb_api.create_workspace(self.token, f'workspace_exceeded_{self.rand_id}')
        workspace_exceeded = User.get_by_id(workspace_exceeded['id'])
        exceeded_token = workspace_exceeded.get_token_for_scope(scopes.ADMIN)
        self._dummy_query_api(exceeded_token, 2)
        self.insert_row_storage_metrics_using_usage_metrics_storage__v2(workspace_exceeded,
                                                                        datetime.combine(date.today(),
                                                                                         datetime.min.time()),
                                                                        10000, self.STORAGE_BYTES_EXCEEDED, 0, 0)
        self.workspaces_to_delete.append(workspace_exceeded)
        self.assertSpans(workspace_exceeded, 2)
        self.assertPipeStats(workspace_exceeded, 2)

        workspace_reaching = self.tb_api.create_workspace(self.token, f'workspace_reaching_{self.rand_id}')
        workspace_reaching = User.get_by_id(workspace_reaching['id'])
        reaching_token = workspace_reaching.get_token_for_scope(scopes.ADMIN)
        self._dummy_query_api(reaching_token, 1)
        self.insert_row_storage_metrics_using_usage_metrics_storage__v2(workspace_reaching,
                                                                        datetime.combine(date.today(),
                                                                                         datetime.min.time()),
                                                                        10000, self.STORAGE_BYTES_REACHING, 0, 0)
        self.workspaces_to_delete.append(workspace_reaching)
        self.assertSpans(workspace_reaching, 1)
        self.assertPipeStats(workspace_reaching, 1)

        workspace_in_plan = self.tb_api.create_workspace(self.token, f'workspace_in_plan_{self.rand_id}')
        workspace_in_plan = User.get_by_id(workspace_in_plan['id'])
        self.insert_row_storage_metrics_using_usage_metrics_storage__v2(workspace_in_plan,
                                                                        datetime.combine(date.today(),
                                                                                         datetime.min.time()),
                                                                        10000, self.STORAGE_BYTES_IN_PLAN, 0, 0)
        self.workspaces_to_delete.append(workspace_in_plan)
        self.assertSpans(workspace_in_plan, 0)
        self.assertPipeStats(workspace_in_plan, 0)

        workspace_not_in_build_plan = self.tb_api.create_workspace(self.token, f'workspace_not_in_build_plan_{self.rand_id}')
        workspace_not_in_build_plan = User.get_by_id(workspace_not_in_build_plan['id'])
        workspace_not_in_build_plan.plan = BillingPlans.PRO
        workspace_not_in_build_plan.save()
        not_in_build_plan_token = workspace_not_in_build_plan.get_token_for_scope(scopes.ADMIN)
        self._dummy_query_api(not_in_build_plan_token, 2)
        self.insert_row_storage_metrics_using_usage_metrics_storage__v2(workspace_not_in_build_plan,
                                                                        datetime.combine(date.today(),
                                                                                         datetime.min.time()),
                                                                        10000, self.STORAGE_BYTES_EXCEEDED, 0, 0)
        self.workspaces_to_delete.append(workspace_not_in_build_plan)
        self.assertSpans(workspace_not_in_build_plan, 2)
        self.assertPipeStats(workspace_not_in_build_plan, 2)

        self.exec_workspace_datatracker([workspace_exceeded, workspace_reaching, workspace_in_plan])

        # mock requests limit
        BuildPlanTracker.MAX_API_REQUESTS_PER_DAY_LIMIT = 1

        MailgunService.send_notification_on_build_plan_limits = AsyncMock(return_value=NotificationResponse(200))

        BuildPlanTracker.track_limits()

        BuildPlanTracker.MAX_API_REQUESTS_PER_DAY_LIMIT = DEFAULT_PLAN_CONFIG[PlanConfigConcepts.DEV_MAX_API_REQUESTS_PER_DAY]

        send_notification_calls = [call([self.user.email], workspace_reaching.id, workspace_reaching.name, 1, 1, 8, 10, 0.07, 0.34, exceeded=False),
                                   call([self.user.email], workspace_exceeded.id, workspace_exceeded.name, 2, 1, 11, 10, 0.07, 0.34, exceeded=True)]

        self.assertEqual(MailgunService.send_notification_on_build_plan_limits.call_count, 2)
        MailgunService.send_notification_on_build_plan_limits.assert_has_calls(send_notification_calls, any_order=True)

    def test_track_build_plan_limits_just_requests(self):
        workspace_reaching = self.tb_api.create_workspace(self.token, f'workspace_reaching_{self.rand_id}')
        workspace_reaching = User.get_by_id(workspace_reaching['id'])
        reaching_token = workspace_reaching.get_token_for_scope(scopes.ADMIN)
        self._dummy_query_api(reaching_token, 1)
        self.insert_row_storage_metrics_using_usage_metrics_storage__v2(workspace_reaching,
                                                                        datetime.combine(date.today(),
                                                                                         datetime.min.time()),
                                                                        10000, self.STORAGE_BYTES_IN_PLAN, 0, 0)
        self.workspaces_to_delete.append(workspace_reaching)
        self.assertSpans(workspace_reaching, 1)
        self.assertPipeStats(workspace_reaching, 1)

        self.exec_workspace_datatracker([workspace_reaching])

        # mock requests limit
        BuildPlanTracker.MAX_API_REQUESTS_PER_DAY_LIMIT = 1

        MailgunService.send_notification_on_build_plan_limits = AsyncMock(return_value=NotificationResponse(200))

        BuildPlanTracker.track_limits()

        BuildPlanTracker.MAX_API_REQUESTS_PER_DAY_LIMIT = DEFAULT_PLAN_CONFIG[
            PlanConfigConcepts.DEV_MAX_API_REQUESTS_PER_DAY]

        send_notification_calls = [
            call([self.user.email], workspace_reaching.id, workspace_reaching.name, 1, 1, None, 10, 0.07, 0.34,
                 exceeded=False)]

        self.assertEqual(MailgunService.send_notification_on_build_plan_limits.call_count, 1)
        MailgunService.send_notification_on_build_plan_limits.assert_has_calls(send_notification_calls, any_order=True)
