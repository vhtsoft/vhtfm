# Copyright (c) 2020, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import time

from werkzeug.wrappers import Response

import vhtfm
import vhtfm.rate_limiter
from vhtfm.rate_limiter import RateLimiter
from vhtfm.tests import IntegrationTestCase
from vhtfm.utils import cint


class TestRateLimiter(IntegrationTestCase):
	def test_apply_with_limit(self):
		vhtfm.conf.rate_limit = {"window": 86400, "limit": 1}
		vhtfm.rate_limiter.apply()

		self.assertTrue(hasattr(vhtfm.local, "rate_limiter"))
		self.assertIsInstance(vhtfm.local.rate_limiter, RateLimiter)

		vhtfm.cache.delete(vhtfm.local.rate_limiter.key)
		delattr(vhtfm.local, "rate_limiter")

	def test_apply_without_limit(self):
		vhtfm.conf.rate_limit = None
		vhtfm.rate_limiter.apply()

		self.assertFalse(hasattr(vhtfm.local, "rate_limiter"))

	def test_respond_over_limit(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		vhtfm.conf.rate_limit = {"window": 86400, "limit": 0.01}
		self.assertRaises(vhtfm.TooManyRequestsError, vhtfm.rate_limiter.apply)
		vhtfm.rate_limiter.update()

		response = vhtfm.rate_limiter.respond()

		self.assertIsInstance(response, Response)
		self.assertEqual(response.status_code, 429)

		headers = vhtfm.local.rate_limiter.headers()
		self.assertIn("Retry-After", headers)
		self.assertNotIn("X-RateLimit-Used", headers)
		self.assertIn("X-RateLimit-Reset", headers)
		self.assertIn("X-RateLimit-Limit", headers)
		self.assertIn("X-RateLimit-Remaining", headers)
		self.assertTrue(int(headers["X-RateLimit-Reset"]) <= 86400)
		self.assertEqual(int(headers["X-RateLimit-Limit"]), 10000)
		self.assertEqual(int(headers["X-RateLimit-Remaining"]), 0)

		vhtfm.cache.delete(limiter.key)
		vhtfm.cache.delete(vhtfm.local.rate_limiter.key)
		delattr(vhtfm.local, "rate_limiter")

	def test_respond_under_limit(self):
		vhtfm.conf.rate_limit = {"window": 86400, "limit": 0.01}
		vhtfm.rate_limiter.apply()
		vhtfm.rate_limiter.update()
		response = vhtfm.rate_limiter.respond()
		self.assertEqual(response, None)

		vhtfm.cache.delete(vhtfm.local.rate_limiter.key)
		delattr(vhtfm.local, "rate_limiter")

	def test_headers_under_limit(self):
		vhtfm.conf.rate_limit = {"window": 86400, "limit": 0.01}
		vhtfm.rate_limiter.apply()
		vhtfm.rate_limiter.update()
		headers = vhtfm.local.rate_limiter.headers()
		self.assertNotIn("Retry-After", headers)
		self.assertIn("X-RateLimit-Reset", headers)
		self.assertTrue(int(headers["X-RateLimit-Reset"] < 86400))
		self.assertEqual(int(headers["X-RateLimit-Used"]), vhtfm.local.rate_limiter.duration)
		self.assertEqual(int(headers["X-RateLimit-Limit"]), 10000)
		self.assertEqual(int(headers["X-RateLimit-Remaining"]), 10000)

		vhtfm.cache.delete(vhtfm.local.rate_limiter.key)
		delattr(vhtfm.local, "rate_limiter")

	def test_reject_over_limit(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		limiter = RateLimiter(0.01, 86400)
		self.assertRaises(vhtfm.TooManyRequestsError, limiter.apply)

		vhtfm.cache.delete(limiter.key)

	def test_do_not_reject_under_limit(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		limiter = RateLimiter(0.02, 86400)
		self.assertEqual(limiter.apply(), None)

		vhtfm.cache.delete(limiter.key)

	def test_update_method(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		self.assertEqual(limiter.duration, cint(vhtfm.cache.get(limiter.key)))

		vhtfm.cache.delete(limiter.key)
