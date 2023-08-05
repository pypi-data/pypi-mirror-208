import unittest

from tinybird.feature_flags import FeatureFlagsService, FeatureFlagBase, FeatureDetails, FeatureFlagsWorkspaceService


class FeatureFlagMock(FeatureFlagBase):
    FULL_ACCESS_ACCOUNT = "full_access_account"
    ONBOARDING = "onboarding"


class TestFeatureFlags(unittest.TestCase):

    _configured_domain = None
    _configured_map_features_and_details = None

    @classmethod
    def setUpClass(cls) -> None:

        cls._configured_domain = FeatureFlagsService.configured_domain
        cls._configured_map_features_and_details = FeatureFlagsService.map_features_and_details

        FeatureFlagsService.configured_domain = 'tinybird.co'

        FeatureFlagsService.map_features_and_details = {
            FeatureFlagMock.FULL_ACCESS_ACCOUNT: FeatureDetails(
                "Feature default false but true for configured domain, hidden", False, override_for_configured_domain=True),
            FeatureFlagMock.ONBOARDING: FeatureDetails(
                "not hidden one", False, private=False, override_for_configured_domain=True),
        }

    @classmethod
    def tearDownClass(cls) -> None:
        FeatureFlagsService.configured_domain = cls._configured_domain
        FeatureFlagsService.map_features_and_details = cls._configured_map_features_and_details
        super().tearDownClass()

    def test_get_existing_feature_for_a_not_configured_domain(self):
        ff_value = FeatureFlagsService.feature_for_email(FeatureFlagMock.FULL_ACCESS_ACCOUNT, 'random@email.com')
        self.assertEqual(False, ff_value)

    def test_get_existing_feature_for_a_not_configured_domain_but_with_config_override(self):
        ff_value = FeatureFlagsService.feature_for_email(FeatureFlagMock.FULL_ACCESS_ACCOUNT, 'random@email.com',
                                                         {FeatureFlagMock.FULL_ACCESS_ACCOUNT.value: True})
        self.assertEqual(True, ff_value)

    def test_get_existing_feature_for_a_configured_domain(self):
        ff_value = FeatureFlagsService.feature_for_email(FeatureFlagMock.FULL_ACCESS_ACCOUNT, 'random@tinybird.co')
        self.assertEqual(True, ff_value)

    def test_get_existing_feature_that_is_overrided(self):
        ff_value = FeatureFlagsService.feature_for_email(FeatureFlagMock.ONBOARDING, 'random@tinybird.co', {FeatureFlagMock.ONBOARDING.value: True})
        self.assertEqual(True, ff_value)

    def test_get_all_features_for_private_listing(self):
        ff_values = FeatureFlagsService.get_all_feature_values('random@email.com', include_private=True)

        self.assertEqual({
            'full_access_account': False,
            'onboarding': False,
        }, ff_values)

    def test_get_all_features_for_public_listing(self):
        ff_values = FeatureFlagsService.get_all_feature_values('random@email.com')

        self.assertEqual({
            'onboarding': False
        }, ff_values)


class FeatureFlagWorkspaceMock(FeatureFlagBase):
    DATASOURCES_OPS_LOG_ENRICHMENT = 'datasources_ops_log_enrichment'
    ENABLE_STORAGE_POLICY = 'enable_storage_policy'


class TestFeatureFlagsWorkspace(unittest.TestCase):

    _configured_map_features_and_details = None

    @classmethod
    def setUpClass(cls) -> None:

        cls._configured_map_features_and_details = FeatureFlagsWorkspaceService.map_features_and_details

        FeatureFlagsWorkspaceService.map_features_and_details = {
            FeatureFlagWorkspaceMock.DATASOURCES_OPS_LOG_ENRICHMENT: FeatureDetails(
                "Enable datasources ops log enrichment", default_value=False,
                private=False),
            FeatureFlagWorkspaceMock.ENABLE_STORAGE_POLICY: FeatureDetails(
                "Enable custom storage policy", default_value=False,
                private=True),
        }

    @classmethod
    def tearDownClass(cls) -> None:
        FeatureFlagsWorkspaceService.map_features_and_details = cls._configured_map_features_and_details
        super().tearDownClass()

    def test_get_existing_feature(self):
        ff_value = FeatureFlagsWorkspaceService.feature_for_id(FeatureFlagWorkspaceMock.DATASOURCES_OPS_LOG_ENRICHMENT, "", None)
        self.assertEqual(False, ff_value)

    def test_get_existing_feature_that_is_overrided(self):
        ff_value = FeatureFlagsWorkspaceService.feature_for_id(FeatureFlagWorkspaceMock.DATASOURCES_OPS_LOG_ENRICHMENT, '', {FeatureFlagWorkspaceMock.DATASOURCES_OPS_LOG_ENRICHMENT.value: True})
        self.assertEqual(True, ff_value)

    def test_get_all_features_for_private_listing(self):
        ff_values = FeatureFlagsWorkspaceService.get_all_feature_values(include_private=True)

        self.assertEqual({
            FeatureFlagWorkspaceMock.DATASOURCES_OPS_LOG_ENRICHMENT.value: False,
            FeatureFlagWorkspaceMock.ENABLE_STORAGE_POLICY.value: False,
        }, ff_values)

    def test_get_all_features_for_public_listing(self):
        ff_values = FeatureFlagsWorkspaceService.get_all_feature_values(include_private=False)

        self.assertEqual({
            FeatureFlagWorkspaceMock.DATASOURCES_OPS_LOG_ENRICHMENT.value: False
        }, ff_values)
