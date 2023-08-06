from datetime import timedelta, datetime
import uuid

from tests.views.base_test import BaseTest, TBApiProxy, STRIPE_SUBSCRIPTION_MOCK
from unittest.mock import patch
from tinybird.job import UsageRecordsTracker
from tinybird.token_scope import scopes
from tinybird.user import User, UserAccount


STRIPE_SUBSCRIPTIONS_MOCK = {'data': [STRIPE_SUBSCRIPTION_MOCK], "has_more": False}


class TestUsageRecordsTracker(BaseTest):
    def setUp(self):
        super(TestUsageRecordsTracker, self).setUp()
        self.tb_api_proxy = TBApiProxy(self)
        self.token = UserAccount.get_by_id(self.USER_ID).get_token_for_scope(scopes.AUTH)
        metrics_cluster = None

        self.usage_records_tracker = UsageRecordsTracker(metrics_cluster=metrics_cluster)

    @patch('stripe.Subscription.list')
    @patch('tinybird.plans.PlansService.track_usage_records', return_value=None)
    def test_track_records(self, plan_track_usage_records_mock, plan_subscriptions_list_mock):
        self.tb_api_proxy.create_customer(self.token, self.WORKSPACE_ID)
        self.tb_api_proxy.setup_payment_intent(self.token, self.WORKSPACE_ID)
        self.tb_api_proxy.subscribe_to_pro(self.token, self.WORKSPACE_ID)

        subscriptions = STRIPE_SUBSCRIPTIONS_MOCK
        subscriptions['data'][0]["metadata"]["workspace_id"] = self.WORKSPACE_ID
        plan_subscriptions_list_mock.return_value.auto_paging_iter.return_value = subscriptions['data']

        self.usage_records_tracker.track_usage_records()

        plan_track_usage_records_mock.assert_called_once_with(User.get_by_id(self.WORKSPACE_ID), STRIPE_SUBSCRIPTION_MOCK,
                                                              metrics_cluster=self.usage_records_tracker.metrics_cluster)

    @patch('stripe.Subscription.list')
    @patch('tinybird.plans.PlansService.track_usage_records', return_value=None)
    def test_do_not_track_records_if_subscription_from_other_region(self, plan_track_usage_records_mock,
                                                                    plan_subscriptions_list_mock):
        self.tb_api_proxy.create_customer(self.token, self.WORKSPACE_ID)
        self.tb_api_proxy.setup_payment_intent(self.token, self.WORKSPACE_ID)
        self.tb_api_proxy.subscribe_to_pro(self.token, self.WORKSPACE_ID)

        subscriptions = STRIPE_SUBSCRIPTIONS_MOCK
        subscriptions['data'][0]["created"] = datetime.timestamp(datetime.now() - timedelta(days=1))
        subscriptions['data'][0]["metadata"]["workspace_id"] = str(uuid.uuid4())
        plan_subscriptions_list_mock.return_value.auto_paging_iter.return_value = subscriptions['data']

        self.usage_records_tracker.track_usage_records()

        plan_track_usage_records_mock.assert_not_called()
