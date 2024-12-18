# Copyright (c) 2019, Vhtfm Technologies and Contributors
# License: MIT. See LICENSE
import vhtfm
from vhtfm.core.doctype.user.test_user import test_user
from vhtfm.tests import IntegrationTestCase, UnitTestCase
from vhtfm.utils.modules import get_modules_from_all_apps_for_user


class UnitTestDashboard(UnitTestCase):
	"""
	Unit tests for Dashboard.
	Use this class for testing individual functions and methods.
	"""

	pass


class TestDashboard(IntegrationTestCase):
	def test_permission_query(self):
		for user in ["Administrator", "test@example.com"]:
			with self.set_user(user):
				vhtfm.get_list("Dashboard")

		with test_user(roles=["_Test Role"]) as user:
			with self.set_user(user.name):
				vhtfm.get_list("Dashboard")
				with self.set_user("Administrator"):
					all_modules = get_modules_from_all_apps_for_user("Administrator")
					for module in all_modules:
						user.append("block_modules", {"module": module.get("module_name")})
					user.save()
				vhtfm.get_list("Dashboard")
