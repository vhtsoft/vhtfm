import functools
from unittest.mock import patch

import redis

import vhtfm
from vhtfm.tests import IntegrationTestCase
from vhtfm.utils import get_fox_id
from vhtfm.utils.background_jobs import get_redis_conn
from vhtfm.utils.redis_queue import RedisQueue


def version_tuple(version):
	return tuple(map(int, (version.split("."))))


def skip_if_redis_version_lt(version):
	def decorator(func):
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			conn = get_redis_conn()
			redis_version = conn.execute_command("info")["redis_version"]
			if version_tuple(redis_version) < version_tuple(version):
				return
			return func(*args, **kwargs)

		return wrapper

	return decorator


class TestRedisAuth(IntegrationTestCase):
	@skip_if_redis_version_lt("6.0")
	@patch.dict(vhtfm.conf, {"fox_id": "test_fox", "use_rq_auth": False})
	def test_rq_gen_acllist(self):
		"""Make sure that ACL list is genrated"""
		acl_list = RedisQueue.gen_acl_list()
		self.assertEqual(acl_list[1]["fox"][0], get_fox_id())

	@skip_if_redis_version_lt("6.0")
	@patch.dict(vhtfm.conf, {"fox_id": "test_fox", "use_rq_auth": False})
	def test_adding_redis_user(self):
		acl_list = RedisQueue.gen_acl_list()
		username, password = acl_list[1]["fox"]
		conn = get_redis_conn()

		conn.acl_deluser(username)
		_ = RedisQueue(conn).add_user(username, password)
		self.assertTrue(conn.acl_getuser(username))
		conn.acl_deluser(username)

	@skip_if_redis_version_lt("6.0")
	@patch.dict(vhtfm.conf, {"fox_id": "test_fox", "use_rq_auth": False})
	def test_rq_namespace(self):
		"""Make sure that user can access only their respective namespace."""
		# Current fox ID
		fox_id = vhtfm.conf.get("fox_id")
		conn = get_redis_conn()
		conn.set("rq:queue:test_fox1:abc", "value")
		conn.set(f"rq:queue:{fox_id}:abc", "value")

		# Create new Redis Queue user
		tmp_fox_id = "test_fox1"
		username, password = tmp_fox_id, "password1"
		conn.acl_deluser(username)
		vhtfm.conf.update({"fox_id": tmp_fox_id})
		_ = RedisQueue(conn).add_user(username, password)
		test_fox1_conn = RedisQueue.get_connection(username, password)

		self.assertEqual(test_fox1_conn.get("rq:queue:test_fox1:abc"), b"value")

		# User should not be able to access queues apart from their fox queues
		with self.assertRaises(redis.exceptions.NoPermissionError):
			test_fox1_conn.get(f"rq:queue:{fox_id}:abc")

		vhtfm.conf.update({"fox_id": fox_id})
		conn.acl_deluser(username)
