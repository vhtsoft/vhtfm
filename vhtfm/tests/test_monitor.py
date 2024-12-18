# Copyright (c) 2020, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import vhtfm
import vhtfm.monitor
from vhtfm.monitor import MONITOR_REDIS_KEY, get_trace_id
from vhtfm.tests import IntegrationTestCase
from vhtfm.utils import set_request
from vhtfm.utils.response import build_response


class TestMonitor(IntegrationTestCase):
	def setUp(self):
		vhtfm.conf.monitor = 1
		vhtfm.cache.delete_value(MONITOR_REDIS_KEY)

	def tearDown(self):
		vhtfm.conf.monitor = 0
		vhtfm.cache.delete_value(MONITOR_REDIS_KEY)

	def test_enable_monitor(self):
		set_request(method="GET", path="/api/method/vhtfm.ping")
		response = build_response("json")

		vhtfm.monitor.start()
		vhtfm.monitor.stop(response)

		logs = vhtfm.cache.lrange(MONITOR_REDIS_KEY, 0, -1)
		self.assertEqual(len(logs), 1)

		log = vhtfm.parse_json(logs[0].decode())
		self.assertTrue(log.duration)
		self.assertTrue(log.site)
		self.assertTrue(log.timestamp)
		self.assertTrue(log.uuid)
		self.assertTrue(log.request)
		self.assertEqual(log.transaction_type, "request")
		self.assertEqual(log.request["method"], "GET")

	def test_no_response(self):
		set_request(method="GET", path="/api/method/vhtfm.ping")

		vhtfm.monitor.start()
		vhtfm.monitor.stop(response=None)

		logs = vhtfm.cache.lrange(MONITOR_REDIS_KEY, 0, -1)
		self.assertEqual(len(logs), 1)

		log = vhtfm.parse_json(logs[0].decode())
		self.assertEqual(log.request["status_code"], 500)
		self.assertEqual(log.transaction_type, "request")
		self.assertEqual(log.request["method"], "GET")

	def test_job(self):
		vhtfm.utils.background_jobs.execute_job(
			vhtfm.local.site, "vhtfm.ping", None, None, {}, is_async=False
		)

		logs = vhtfm.cache.lrange(MONITOR_REDIS_KEY, 0, -1)
		self.assertEqual(len(logs), 1)
		log = vhtfm.parse_json(logs[0].decode())
		self.assertEqual(log.transaction_type, "job")
		self.assertTrue(log.job)
		self.assertEqual(log.job["method"], "vhtfm.ping")
		self.assertEqual(log.job["scheduled"], False)
		self.assertEqual(log.job["wait"], 0)

	def test_flush(self):
		set_request(method="GET", path="/api/method/vhtfm.ping")
		response = build_response("json")
		vhtfm.monitor.start()
		vhtfm.monitor.stop(response)

		open(vhtfm.monitor.log_file(), "w").close()
		vhtfm.monitor.flush()

		with open(vhtfm.monitor.log_file()) as f:
			logs = f.readlines()

		self.assertEqual(len(logs), 1)
		log = vhtfm.parse_json(logs[0])
		self.assertEqual(log.transaction_type, "request")

	def test_trace_ids(self):
		set_request(method="GET", path="/api/method/vhtfm.ping")
		response = build_response("json")
		vhtfm.monitor.start()
		vhtfm.db.sql("select 1")
		self.assertIn(get_trace_id(), str(vhtfm.db.last_query))
		vhtfm.monitor.stop(response)
