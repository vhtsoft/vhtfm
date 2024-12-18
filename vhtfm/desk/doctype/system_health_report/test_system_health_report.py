# Copyright (c) 2024, Vhtfm Technologies and Contributors
# See license.txt

import vhtfm
from vhtfm.tests import IntegrationTestCase, UnitTestCase


class UnitTestSystemHealthReport(UnitTestCase):
	"""
	Unit tests for SystemHealthReport.
	Use this class for testing individual functions and methods.
	"""

	pass


class TestSystemHealthReport(IntegrationTestCase):
	def test_it_works(self):
		vhtfm.get_doc("System Health Report")
