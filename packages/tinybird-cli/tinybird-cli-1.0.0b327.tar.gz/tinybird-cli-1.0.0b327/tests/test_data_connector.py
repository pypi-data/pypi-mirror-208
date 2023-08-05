import uuid

import atexit
import os
import sys
from unittest import mock
import tornado.testing
import subprocess
from unittest.mock import patch

from tinybird.kafka_utils import KafkaUtils
from .views.base_test import BaseTest
import shutil

from tinybird import data_connector
from tinybird.user import UserAccount, User

KAFKA_PATH = os.environ.get('KAFKA_PATH', os.path.join(os.path.dirname(__file__), '../..', 'kafka_2.13-2.8.0'))


class TestKafka(BaseTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        shutil.rmtree('/tmp/kafka-logs-test', ignore_errors=True)
        shutil.rmtree('/tmp/zookeeper-kafka-test', ignore_errors=True)

        args = (
            f'{KAFKA_PATH}/bin/zookeeper-server-start.sh',
            os.path.join(os.path.dirname(__file__), '..', './tests/kafka-zookeeper-test.properties')
        )
        cls.zookeeper_process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=sys.stdout, universal_newlines=True)

        @atexit.register
        def kill_zk():
            cls.zookeeper_process.kill()

        found = False
        while not found:
            if cls.zookeeper_process.poll() is not None:
                break
            for line in iter(cls.zookeeper_process.stdout.readline, ''):
                if line.find('Using checkInterval') != -1:
                    print("ZK started!")
                    found = True
                    break
                if line.find('Unexpected exception') != -1:
                    print("Could not start ZK process: " + line.rstrip())
                    cls.assertTrue(False, None, msg="ZK process not started")
                    return

        args = (
            f'{KAFKA_PATH}/bin/kafka-server-start.sh',
            os.path.join(os.path.dirname(__file__), '..', './tests/kafka-test-server.properties')
        )
        cls.kafka_process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=sys.stdout, universal_newlines=True)

        @atexit.register
        def kill_kafka():
            cls.kafka_process.kill()

        found = False
        while not found:
            if cls.kafka_process.poll() is not None:
                break

            for line in iter(cls.kafka_process.stdout.readline, ''):
                if line.find('Recorded new controller') != -1:
                    print("KAFKA server started : " + line.rstrip())
                    found = True
                    break
                if line.find('Unexpected exception') != -1:
                    print("Could not start Kafka process: " + line.rstrip())
                    cls.assertTrue(False, None, msg="Kafka process not started")
                    return

        cls.zookeeper_process.stdout.close()
        cls.kafka_process.stdout.close()

    def setUp(self):
        super().setUp()
        self.assertEqual(self.zookeeper_process.poll(), None, msg="ZK process could not start")
        self.assertEqual(self.kafka_process.poll(), None, msg="Kafka process could not start")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.kafka_process.kill()
        cls.zookeeper_process.kill()

    def produce_message(self, message, topic):
        producer_cmd = f"""{KAFKA_PATH}/bin/kafka-console-producer.sh --bootstrap-server localhost:9093 \
                            --topic {topic} --timeout 10 --producer-property enable.idempotence=true \
                            --request-required-acks -1 2>/dev/null"""

        c = os.system(f'''echo {message} | {producer_cmd}''')
        self.assertEqual(c, 0)

    def create_kafka_connector(self):
        user_account = UserAccount.register(f'test_kafka_preview{uuid.uuid4().hex}@mail', 'pass')
        workspace = self.register_workspace(f'test_kafka_preview_ws_{uuid.uuid4().hex}', user_account.id)

        conn = data_connector.DataConnector.add_connector(user=workspace, name="name", service='kafka', settings={
            'kafka_bootstrap_servers': 'localhost:9093',
            'kafka_security_protocol': 'plaintext',
            'kafka_sasl_plain_username': '',
            'kafka_sasl_plain_password': '',
        })

        return conn

    @tornado.testing.gen_test
    @patch('tinybird.data_connector.KafkaSettings.PREVIEW_POLL_TIMEOUT_MS', 2000)
    async def test_kafka_preview_all_params_happy(self):
        self.produce_message("""'{"test": 3}'""", "kafkafirst")
        conn = self.create_kafka_connector()
        r = await KafkaUtils.get_kafka_preview(conn,
                                               'test_groupid',
                                               kafka_topics=['kafkafirst'])
        assert r.get('error', None) is None
        output = r['preview']
        expected_deserialization = {
            'data': [{'test': 3}],
            'meta': [{'name': 'test', 'type': 'Int16'}],
            'rows': 1,
            'statistics': mock.ANY
        }
        self.assertEqual(len(output), 1)
        t = output[0]
        assert t['deserialized'] == expected_deserialization
        self.assertEqual(t['topic'], 'kafkafirst')
        self.assertEqual(t['messages_in_last_hour'], 1)
        last = t['last_messages']
        self.assertEqual(len(last), 1)
        self.assertEqual(last[0]['__partition'], 0)
        self.assertEqual(last[0]['__offset'], 0)
        self.assertEqual(last[0]['__key'], None)
        self.assertEqual(last[0]['__value'], '''{"test": 3}''')

    @tornado.testing.gen_test
    async def test_kafka_preview_topic_notexists(self):
        conn = self.create_kafka_connector()
        r = await KafkaUtils.get_kafka_preview(conn,
                                               'test_groupid',
                                               kafka_topics=['kafka_not_exists123'],
                                               preview_activity=True)
        self.assertEqual(r['error'], 'not_exists')

    @tornado.testing.gen_test
    @patch('tinybird.data_connector.KafkaSettings.PREVIEW_POLL_TIMEOUT_MS', 2000)
    async def test_kafka_preview_connector_id(self):
        self.produce_message("msg2", "kafkasecond")
        conn = self.create_kafka_connector()

        r = await KafkaUtils.get_kafka_preview(data_connector=conn, kafka_group_id='test_groupid', kafka_topics=['kafkasecond'])
        output = r['preview']
        self.assertEqual(len(output), 1)
        t = output[0]
        self.assertEqual(t['topic'], 'kafkasecond')
        self.assertEqual(t['messages_in_last_hour'], 1)
        self.assertEqual(t['committed'], False)
        last = t['last_messages']
        self.assertEqual(len(last), 1)
        self.assertEqual(last[0]['__partition'], 0)
        self.assertEqual(last[0]['__offset'], 0)
        self.assertEqual(last[0]['__key'], None)
        self.assertEqual(last[0]['__value'], "msg2")


class TestKafkaInvalidParams(BaseTest):
    @tornado.testing.gen_test
    @patch('tinybird.data_connector.KafkaSettings.PREVIEW_POLL_TIMEOUT_MS', 10)
    async def test_kafka_preview_all_params_invalid(self):
        user_account = UserAccount.register(f'test_kafka_preview{uuid.uuid4().hex}@mail', 'pass')
        workspace = self.register_workspace(f'test_kafka_preview_ws_{uuid.uuid4().hex}', user_account.id)

        conn = data_connector.DataConnector.add_connector(user=workspace, name="name", service='kafka', settings={
            'kafka_bootstrap_servers': 'localhost:49999',
            'kafka_security_protocol': 'plaintext',
            'kafka_sasl_plain_username': '',
            'kafka_sasl_plain_password': '',
        })

        output = await KafkaUtils.get_kafka_preview(conn,
                                                    'test_groupid')
        self.assertTrue('error' in output)


class TestGCloudScheduler(BaseTest):
    def test_create_data_connector_for_gcscheduler(self):
        connector_name = 'test_gcloud_connector'
        pipe_name = 'test_glcoud_connector_pipe'
        self.workspace = User.get_by_id(self.WORKSPACE_ID)
        copy_pipe = self.workspace.add_pipe(pipe_name, 'SELECT * FROM test_table')

        connector = data_connector.DataConnector.add_connector(
            user=self.workspace,
            name=connector_name,
            service=data_connector.DataConnectors.GCLOUD_SCHEDULER,
            settings={}
        )

        sink = data_connector.DataSink.add_sink(
            data_connector=connector,
            resource=copy_pipe,
            settings={}
        )

        self.assertEqual(sink.data_connector_id, connector.id)

        sink_by_pipe = data_connector.DataSink.get_by_pipe_id(copy_pipe.id)
        self.assertEqual(sink_by_pipe.id, sink.id)


class TestSnowflakeConnector(BaseTest):
    def test_create_snowflake_data_connector_fails_with_no_settings(self):
        connector_name = 'test_snowflake_connector'
        self.workspace = User.get_by_id(self.WORKSPACE_ID)
        with self.assertRaises(data_connector.InvalidSettingsException):
            _ = data_connector.DataConnector.add_connector(
                user=self.workspace,
                name=connector_name,
                service=data_connector.DataConnectors.SNOWFLAKE,
                settings={}
            )

    def test_create_snowflake_data_connector_succeeds_with_all_settings(self):
        connector_name = 'test_snowflake_connector'
        self.workspace = User.get_by_id(self.WORKSPACE_ID)
        settings = {
            'account': 'sf_account',
            'username': 'sf_username',
            'password': 'sf_password',
            'role': 'sf_role',
            'warehouse': 'sf_warehouse',
            'warehouse_size': 'X-Small',
        }
        connector = data_connector.DataConnector.add_connector(
            user=self.workspace,
            name=connector_name,
            service=data_connector.DataConnectors.SNOWFLAKE,
            settings=settings
        )

        self.assertEqual(connector.settings, settings)

    def test_create_snowflake_data_connector_succeeds_with_mandatory_settings(self):
        connector_name = 'test_snowflake_connector'
        self.workspace = User.get_by_id(self.WORKSPACE_ID)
        settings = {
            'account': 'sf_account',
            'username': 'sf_username',
            'password': 'sf_password',
            'role': 'sf_role',
            'warehouse': 'sf_warehouse',
        }
        connector = data_connector.DataConnector.add_connector(
            user=self.workspace,
            name=connector_name,
            service=data_connector.DataConnectors.SNOWFLAKE,
            settings=settings
        )

        self.assertEqual(connector.settings, settings)

    def test_create_snowflake_data_connector_fails_without_all_mandatory_settings(self):
        connector_name = 'test_snowflake_connector'
        self.workspace = User.get_by_id(self.WORKSPACE_ID)

        def _test(settings):
            with self.assertRaises(data_connector.InvalidSettingsException):
                _ = data_connector.DataConnector.add_connector(
                    user=self.workspace,
                    name=connector_name,
                    service=data_connector.DataConnectors.SNOWFLAKE,
                    settings=settings
                )

        _test({'username': 'sf_username', 'password': 'sf_password'})
        _test({'account': 'sf_account', 'password': 'sf_password'})
        _test({'account': 'sf_account', 'username': 'sf_username'})
        _test({'account': 'sf_account', 'username': 'sf_username', 'password': 'sf_password'})
        _test({'account': 'sf_account', 'username': 'sf_username', 'password': 'sf_password', 'role': 'sf_role'})
        _test({'account': 'sf_account', 'username': 'sf_username', 'password': 'sf_password', 'warehouse': 'warehouse'})
