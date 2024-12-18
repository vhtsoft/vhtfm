"""
This file contains multiple primitive tests for avoiding performance regressions.

- Time bound tests: Foxmarks are done on GHA before adding numbers
- Query count tests: More than expected # of queries for any action is frequent source of
  performance issues. This guards against such problems.


E.g. We know get_controller is supposed to be cached and hence shouldn't make query post first
query. This test can be written like this.

>>> def test_controller_caching(self):
>>>
>>> 	get_controller("User")  # <- "warm up code"
>>> 	with self.assertQueryCount(0):
>>> 		get_controller("User")

"""

import gc
import sys
import time
from unittest.mock import patch

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

import vhtfm
from vhtfm.vhtfmclient import VhtfmClient
from vhtfm.model.base_document import get_controller
from vhtfm.query_builder.utils import db_type_is
from vhtfm.tests import IntegrationTestCase
from vhtfm.tests.test_api import VhtfmAPITestCase
from vhtfm.tests.test_query_builder import run_only_if
from vhtfm.utils import cint
from vhtfm.utils.caching import redis_cache
from vhtfm.website.path_resolver import PathResolver

TEST_USER = "test@example.com"


@run_only_if(db_type_is.MARIADB)
class TestPerformance(IntegrationTestCase):
	def reset_request_specific_caches(self):
		# To simulate close to request level of handling
		vhtfm.destroy()  # releases everything on vhtfm.local
		vhtfm.init(self.TEST_SITE)
		vhtfm.connect()
		vhtfm.clear_cache()

	def setUp(self) -> None:
		self.HOST = vhtfm.utils.get_site_url(vhtfm.local.site)

		self.reset_request_specific_caches()

	def test_meta_caching(self):
		vhtfm.clear_cache()
		vhtfm.get_meta("User")
		vhtfm.clear_cache(doctype="ToDo")

		with self.assertQueryCount(0):
			vhtfm.get_meta("User")

	def test_permitted_fieldnames(self):
		vhtfm.clear_cache()

		doc = vhtfm.new_doc("Prepared Report")
		# load permitted fieldnames once
		doc.permitted_fieldnames

		with patch("vhtfm.model.base_document.get_permitted_fields") as mocked:
			doc.as_dict()
			# get_permitted_fields should not be called again
			mocked.assert_not_called()

	def test_set_value_query_count(self):
		vhtfm.db.set_value("User", "Administrator", "interest", "Nothing")

		with self.assertQueryCount(1):
			vhtfm.db.set_value("User", "Administrator", "interest", "Nothing")

		with self.assertQueryCount(1):
			vhtfm.db.set_value("User", {"user_type": "System User"}, "interest", "Nothing")

		with self.assertQueryCount(1):
			vhtfm.db.set_value(
				"User", {"user_type": "System User"}, {"interest": "Nothing", "bio": "boring person"}
			)

	def test_controller_caching(self):
		get_controller("User")
		with self.assertQueryCount(0):
			get_controller("User")

	def test_get_value_limits(self):
		# check both dict and list style filters
		filters = [{"enabled": 1}, [["enabled", "=", 1]]]

		# Warm up code
		vhtfm.db.get_values("User", filters=filters[0], limit=1)
		for filter in filters:
			with self.assertRowsRead(1):
				self.assertEqual(1, len(vhtfm.db.get_values("User", filters=filter, limit=1)))
			with self.assertRowsRead(2):
				self.assertEqual(2, len(vhtfm.db.get_values("User", filters=filter, limit=2)))

			self.assertEqual(
				len(vhtfm.db.get_values("User", filters=filter)), vhtfm.db.count("User", filter)
			)

			with self.assertRowsRead(1):
				vhtfm.db.get_value("User", filters=filter)

			with self.assertRowsRead(1):
				vhtfm.db.exists("User", filter)

	def test_db_value_cache(self):
		"""Link validation if repeated should just use db.value_cache, hence no extra queries"""
		doc = vhtfm.get_last_doc("User")
		doc.get_invalid_links()

		with self.assertQueryCount(0):
			doc.get_invalid_links()

	@retry(
		retry=retry_if_exception_type(AssertionError),
		stop=stop_after_attempt(3),
		wait=wait_fixed(0.5),
		reraise=True,
	)
	def test_req_per_seconds_basic(self):
		"""Ideally should be ran against gunicorn worker, though I have not seen any difference
		when using werkzeug's run_simple for synchronous requests."""

		EXPECTED_RPS = 120  # measured on GHA
		FAILURE_THREASHOLD = 0.1

		req_count = 1000
		client = VhtfmClient(self.HOST, "Administrator", self.ADMIN_PASSWORD)

		start = time.perf_counter()
		for _ in range(req_count):
			client.get_list("ToDo", limit_page_length=1)
		end = time.perf_counter()

		rps = req_count / (end - start)

		print(f"Completed {req_count} in {end - start} @ {rps} requests per seconds")
		self.assertGreaterEqual(
			rps,
			EXPECTED_RPS * (1 - FAILURE_THREASHOLD),
			"Possible performance regression in basic /api/Resource list  requests",
		)

	def test_homepage_resolver(self):
		paths = ["/", "/app"]
		for path in paths:
			PathResolver(path).resolve()
			with self.assertQueryCount(1):
				PathResolver(path).resolve()

	def test_consistent_build_version(self):
		from vhtfm.utils import get_build_version

		self.assertEqual(get_build_version(), get_build_version())

	def test_get_list_single_query(self):
		"""get_list should only perform single query."""

		user = vhtfm.get_doc("User", TEST_USER)

		vhtfm.set_user(TEST_USER)
		# Give full read access, no share/user perm check should be done.
		user.add_roles("System Manager")

		vhtfm.get_list("User")
		with self.assertQueryCount(1):
			vhtfm.get_list("User")

	def test_no_ifnull_checks(self):
		query = vhtfm.get_all("DocType", {"autoname": ("is", "set")}, run=0).lower()
		self.assertNotIn("coalesce", query)
		self.assertNotIn("ifnull", query)

	def test_no_stale_ref_sql(self):
		"""vhtfm.db.sql should not hold any internal references to result set.

		pymysql stores results internally. If your code reads a lot and doesn't make another
		query, for that entire duration there's copy of result consuming memory in internal
		attributes of pymysql.
		We clear it manually, this test ensures that it actually works.
		"""

		query = "select * from tabUser"
		for kwargs in ({}, {"as_dict": True}, {"as_list": True}):
			result = vhtfm.db.sql(query, **kwargs)
			self.assertEqual(sys.getrefcount(result), 2)  # Note: This always returns +1
			self.assertFalse(gc.get_referrers(result))

	def test_no_cyclic_references(self):
		doc = vhtfm.get_doc("User", "Administrator")
		self.assertEqual(sys.getrefcount(doc), 2)  # Note: This always returns +1

	def test_get_doc_cache_calls(self):
		vhtfm.get_doc("User", "Administrator")
		with self.assertRedisCallCounts(0):
			vhtfm.get_doc("User", "Administrator")

	def test_local_caching(self):
		vhtfm.get_cached_doc("User", "Administrator")
		with self.assertRedisCallCounts(0):
			vhtfm.get_cached_doc("User", "Administrator")

	def test_redis_cache_calls(self):
		redis_cached_func()  # warmup

		# Repeat call should use locally cached value
		with self.assertRedisCallCounts(0):
			redis_cached_func()

		vhtfm.local.cache.clear()
		# Without local cache - only one call required
		with self.assertRedisCallCounts(1):
			redis_cached_func()

	def test_one_time_setup(self):
		site = vhtfm.local.site
		vhtfm.init(site, force=True)
		run = vhtfm.qb._BuilderClasss.run

		vhtfm.init(site, force=True)
		patched_run = vhtfm.qb._BuilderClasss.run

		self.assertIs(run, patched_run, "vhtfm.init should run one-time patching code just once")


@run_only_if(db_type_is.MARIADB)
class TestOverheadCalls(VhtfmAPITestCase):
	"""Test that typical redis and db calls remain same overtime.

	If this tests fail on your PR, make sure you're not introducing something in hot-path of these
	endpoints. Only update values if you're really sure that's the right call.
	Every call increase here is an actual increase in cost!
	"""

	BASE_SQL_CALLS = 2  # rollback + begin

	def test_ping_overheads(self):
		self.get(self.method("ping"), {"sid": "Guest"})
		with self.assertRedisCallCounts(13), self.assertQueryCount(self.BASE_SQL_CALLS):
			self.get(self.method("ping"), {"sid": "Guest"})

	def test_list_view_overheads(self):
		sid = self.sid
		self.get(self.resource("ToDo"), {"sid": sid})
		self.get(self.resource("ToDo"), {"sid": sid})
		with self.assertRedisCallCounts(24), self.assertQueryCount(self.BASE_SQL_CALLS + 1):
			self.get(self.resource("ToDo"), {"sid": sid})

	def test_get_doc_overheads(self):
		sid = self.sid
		tables = len(vhtfm.get_meta("User").get_table_fields())
		self.get(self.resource("User", "Administrator"), {"sid": sid})
		self.get(self.resource("User", "Administrator"), {"sid": sid})
		with self.assertRedisCallCounts(19), self.assertQueryCount(self.BASE_SQL_CALLS + 1 + tables):
			self.get(self.resource("User", "Administrator"), {"sid": sid})


@redis_cache
def redis_cached_func():
	return 42
