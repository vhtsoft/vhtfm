# Copyright (c) 2015, Vhtfm Technologies and Contributors
# License: MIT. See LICENSE
import time

import vhtfm
from vhtfm.auth import CookieManager, LoginManager
from vhtfm.tests import IntegrationTestCase, UnitTestCase


class UnitTestActivityLog(UnitTestCase):
	"""
	Unit tests for ActivityLog.
	Use this class for testing individual functions and methods.
	"""

	pass


class TestActivityLog(IntegrationTestCase):
	def setUp(self) -> None:
		vhtfm.set_user("Administrator")

	def test_activity_log(self):
		# test user login log
		vhtfm.local.form_dict = vhtfm._dict(
			{
				"cmd": "login",
				"sid": "Guest",
				"pwd": self.ADMIN_PASSWORD or "admin",
				"usr": "Administrator",
			}
		)

		vhtfm.local.request_ip = "127.0.0.1"
		vhtfm.local.cookie_manager = CookieManager()
		vhtfm.local.login_manager = LoginManager()

		auth_log = self.get_auth_log()
		self.assertFalse(vhtfm.form_dict.pwd)
		self.assertEqual(auth_log.status, "Success")

		# test user logout log
		vhtfm.local.login_manager.logout()
		auth_log = self.get_auth_log(operation="Logout")
		self.assertEqual(auth_log.status, "Success")

		# test invalid login
		vhtfm.form_dict.update({"pwd": "password"})
		self.assertRaises(vhtfm.AuthenticationError, LoginManager)
		auth_log = self.get_auth_log()
		self.assertEqual(auth_log.status, "Failed")

		vhtfm.local.form_dict = vhtfm._dict()

	def get_auth_log(self, operation="Login"):
		names = vhtfm.get_all(
			"Activity Log",
			filters={
				"user": "Administrator",
				"operation": operation,
			},
			order_by="`creation` DESC",
		)

		name = names[0]
		return vhtfm.get_doc("Activity Log", name)

	def test_brute_security(self):
		update_system_settings({"allow_consecutive_login_attempts": 3, "allow_login_after_fail": 5})

		vhtfm.local.form_dict = vhtfm._dict(
			{"cmd": "login", "sid": "Guest", "pwd": self.ADMIN_PASSWORD, "usr": "Administrator"}
		)

		vhtfm.local.request_ip = "127.0.0.1"
		vhtfm.local.cookie_manager = CookieManager()
		vhtfm.local.login_manager = LoginManager()

		auth_log = self.get_auth_log()
		self.assertEqual(auth_log.status, "Success")

		# test user logout log
		vhtfm.local.login_manager.logout()
		auth_log = self.get_auth_log(operation="Logout")
		self.assertEqual(auth_log.status, "Success")

		# test invalid login
		vhtfm.form_dict.update({"pwd": "password"})
		self.assertRaises(vhtfm.AuthenticationError, LoginManager)
		self.assertRaises(vhtfm.AuthenticationError, LoginManager)
		self.assertRaises(vhtfm.AuthenticationError, LoginManager)

		# REMOVE ME: current logic allows allow_consecutive_login_attempts+1 attempts
		# before raising security exception, remove below line when that is fixed.
		self.assertRaises(vhtfm.AuthenticationError, LoginManager)
		self.assertRaises(vhtfm.SecurityException, LoginManager)
		time.sleep(5)
		self.assertRaises(vhtfm.AuthenticationError, LoginManager)

		vhtfm.local.form_dict = vhtfm._dict()


def update_system_settings(args):
	doc = vhtfm.get_doc("System Settings")
	doc.update(args)
	doc.flags.ignore_mandatory = 1
	doc.save()
