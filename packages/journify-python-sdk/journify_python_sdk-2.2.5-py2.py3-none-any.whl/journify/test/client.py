from datetime import datetime
import unittest

from journify.client import Client
from journify.version import VERSION

if __name__ == '__main__':
    unittest.main()


class TestClient(unittest.TestCase):

    def fail(self, msg=None):
        """Mark the failure handler"""
        self.failed = True

    def setUp(self):
        self.failed = False
        self.client = Client('wk_test_2N0WZTEtnQZxBwdvrdMUJwFyIa1', on_error=self.fail, debug=True)

    def test_requires_write_key(self):
        self.assertRaises(AssertionError, Client)

    def test_empty_flush(self):
        self.client.flush()

    def test_basic_track(self):
        client = self.client
        success, msg = client.track('userId', 'python test event')
        client.flush()
        self.assertTrue(success)
        self.assertFalse(self.failed)

        self.assertEqual(msg['event'], 'python test event')
        self.assertTrue(isinstance(msg['timestamp'], str))
        self.assertTrue(isinstance(msg['messageId'], str))
        self.assertEqual(msg['userId'], 'userId')
        self.assertEqual(msg['properties'], {})
        self.assertEqual(msg['type'], 'track')

    def test_stringifies_user_id(self):
        # A large number that loses precision in node:
        # node -e "console.log(157963456373623802 + 1)" > 157963456373623800
        client = self.client
        success, msg = client.track(
            user_id=157963456373623802, event='python test event')
        client.flush()
        self.assertTrue(success)
        self.assertFalse(self.failed)

        self.assertEqual(msg['userId'], '157963456373623802')
        self.assertEqual(msg['anonymousId'], None)

    def test_stringifies_anonymous_id(self):
        # A large number that loses precision in node:
        # node -e "console.log(157963456373623803 + 1)" > 157963456373623800
        client = self.client
        success, msg = client.track(
            anonymous_id=157963456373623803, event='python test event')
        client.flush()
        self.assertTrue(success)
        self.assertFalse(self.failed)

        self.assertEqual(msg['userId'], None)
        self.assertEqual(msg['anonymousId'], '157963456373623803')

    def test_advanced_track(self):
        client = self.client
        success, msg = client.track('userId', 'python test event', {'property': 'value'},
            {'ip': '192.168.0.1'}, datetime(2014, 9, 3), 'anonymousId', 'messageId')

        self.assertTrue(success)

        self.assertEqual(msg['timestamp'], '2014-09-03T00:00:00+00:00')
        self.assertEqual(msg['properties'], {'property': 'value'})
        self.assertEqual(msg['context']['ip'], '192.168.0.1')
        self.assertEqual(msg['event'], 'python test event')
        self.assertEqual(msg['anonymousId'], 'anonymousId')
        self.assertEqual(msg['context']['library'], {
            'name': 'journify-python-sdk',
            'version': VERSION
        })
        self.assertEqual(msg['messageId'], 'messageId')
        self.assertEqual(msg['userId'], 'userId')
        self.assertEqual(msg['type'], 'track')

    def test_basic_identify(self):
        client = self.client
        success, msg = client.identify('userId', {'trait': 'value'})
        client.flush()
        self.assertTrue(success)
        self.assertFalse(self.failed)

        self.assertEqual(msg['traits'], {'trait': 'value'})
        self.assertTrue(isinstance(msg['timestamp'], str))
        self.assertTrue(isinstance(msg['messageId'], str))
        self.assertEqual(msg['userId'], 'userId')
        self.assertEqual(msg['type'], 'identify')

    def test_advanced_identify(self):
        client = self.client
        success, msg = client.identify(
            'userId', {'trait': 'value'}, {'ip': '192.168.0.1'},
            datetime(2014, 9, 3), 'anonymousId', 'messageId')

        self.assertTrue(success)

        self.assertEqual(msg['timestamp'], '2014-09-03T00:00:00+00:00')
        self.assertEqual(msg['context']['ip'], '192.168.0.1')
        self.assertEqual(msg['traits'], {'trait': 'value'})
        self.assertEqual(msg['anonymousId'], 'anonymousId')
        self.assertEqual(msg['context']['library'], {
            'name': 'journify-python-sdk',
            'version': VERSION
        })
        self.assertTrue(isinstance(msg['timestamp'], str))
        self.assertEqual(msg['messageId'], 'messageId')
        self.assertEqual(msg['userId'], 'userId')
        self.assertEqual(msg['type'], 'identify')

    def test_basic_group(self):
        client = self.client
        success, msg = client.group('userId', 'groupId')
        client.flush()
        self.assertTrue(success)
        self.assertFalse(self.failed)

        self.assertEqual(msg['groupId'], 'groupId')
        self.assertEqual(msg['userId'], 'userId')
        self.assertEqual(msg['type'], 'group')

    def test_advanced_group(self):
        client = self.client
        success, msg = client.group(
            'userId', 'groupId', {'trait': 'value'}, {'ip': '192.168.0.1'},
            datetime(2014, 9, 3), 'anonymousId', 'messageId')

        self.assertTrue(success)

        self.assertEqual(msg['timestamp'], '2014-09-03T00:00:00+00:00')
        self.assertEqual(msg['context']['ip'], '192.168.0.1')
        self.assertEqual(msg['traits'], {'trait': 'value'})
        self.assertEqual(msg['anonymousId'], 'anonymousId')
        self.assertEqual(msg['context']['library'], {
            'name': 'journify-python-sdk',
            'version': VERSION
        })
        self.assertTrue(isinstance(msg['timestamp'], str))
        self.assertEqual(msg['messageId'], 'messageId')
        self.assertEqual(msg['userId'], 'userId')
        self.assertEqual(msg['type'], 'group')

    def test_basic_page(self):
        client = self.client
        success, msg = client.page('userId', name='name')
        self.assertFalse(self.failed)
        client.flush()
        self.assertTrue(success)
        self.assertEqual(msg['userId'], 'userId')
        self.assertEqual(msg['type'], 'page')
        self.assertEqual(msg['name'], 'name')

    def test_advanced_page(self):
        client = self.client
        success, msg = client.page(
            'userId', 'category', 'name', {'property': 'value'},
            {'ip': '192.168.0.1'}, datetime(2014, 9, 3), 'anonymousId', 'messageId')

        self.assertTrue(success)

        self.assertEqual(msg['timestamp'], '2014-09-03T00:00:00+00:00')
        self.assertEqual(msg['context']['ip'], '192.168.0.1')
        self.assertEqual(msg['properties'], {'property': 'value'})
        self.assertEqual(msg['anonymousId'], 'anonymousId')
        self.assertEqual(msg['context']['library'], {
            'name': 'journify-python-sdk',
            'version': VERSION
        })
        self.assertEqual(msg['category'], 'category')
        self.assertTrue(isinstance(msg['timestamp'], str))
        self.assertEqual(msg['messageId'], 'messageId')
        self.assertEqual(msg['userId'], 'userId')
        self.assertEqual(msg['type'], 'page')
        self.assertEqual(msg['name'], 'name')

    def test_flush(self):
        client = self.client
        # set up the consumer with more requests than a single batch will allow
        for _ in range(1000):
            _, _ = client.identify('userId', {'trait': 'value'})
        # We can't reliably assert that the queue is non-empty here; that's
        # a race condition. We do our best to load it up though.
        client.flush()
        # Make sure that the client queue is empty after flushing
        self.assertTrue(client.queue.empty())

    def test_shutdown(self):
        client = self.client
        # set up the consumer with more requests than a single batch will allow
        for _ in range(1000):
            _, _ = client.identify('userId', {'trait': 'value'})
        client.shutdown()
        # we expect two things after shutdown:
        # 1. client queue is empty
        # 2. consumer thread has stopped
        self.assertTrue(client.queue.empty())
        for consumer in client.consumers:
            self.assertFalse(consumer.is_alive())

    def test_synchronous(self):
        client = Client('wk_test_2N0WZTEtnQZxBwdvrdMUJwFyIa1', sync_mode=True)

        success, _ = client.identify('userId')
        self.assertFalse(client.consumers)
        self.assertTrue(client.queue.empty())
        self.assertTrue(success)

    def test_overflow(self):
        client = Client('wk_test_2N0WZTEtnQZxBwdvrdMUJwFyIa1', max_queue_size=1)
        # Ensure consumer thread is no longer uploading
        client.join()

        for _ in range(10):
            client.identify('userId')

        success, _ = client.identify('userId')
        # Make sure we are informed that the queue is at capacity
        self.assertFalse(success)

    def test_success_on_invalid_write_key(self):
        client = Client('bad_key', on_error=self.fail)
        client.track('userId', 'event')
        client.flush()
        self.assertFalse(self.failed)

    def test_unicode(self):
        Client('unicode_key')

    def test_numeric_user_id(self):
        self.client.track(1234, 'python event')
        self.client.flush()
        self.assertFalse(self.failed)

    def test_debug(self):
        Client('bad_key')

    def test_gzip(self):
        client = Client('wk_test_2N0WZTEtnQZxBwdvrdMUJwFyIa1', on_error=self.fail, gzip=True)
        for _ in range(10):
            client.identify('userId', {'trait': 'value'})
        client.flush()
        self.assertFalse(self.failed)

    def test_user_defined_timeout(self):
        client = Client('wk_test_2N0WZTEtnQZxBwdvrdMUJwFyIa1', timeout=10)
        for consumer in client.consumers:
            self.assertEqual(consumer.timeout, 10)

    def test_default_timeout_15(self):
        client = Client('wk_test_2N0WZTEtnQZxBwdvrdMUJwFyIa1')
        for consumer in client.consumers:
            self.assertEqual(consumer.timeout, 15)

    def test_proxies(self):
        client = Client('wk_test_2N0WZTEtnQZxBwdvrdMUJwFyIa1', proxies='203.243.63.16:80')
        success, _ = client.identify('userId', {'trait': 'value'})
        self.assertTrue(success)
