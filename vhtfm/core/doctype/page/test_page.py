# Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import os
import unittest
from unittest.mock import patch

import vhtfm
from vhtfm.tests import IntegrationTestCase, UnitTestCase


class UnitTestPage(UnitTestCase):
	"""
	Unit tests for Page.
	Use this class for testing individual functions and methods.
	"""

	pass


class TestPage(IntegrationTestCase):
	def test_naming(self):
		self.assertRaises(
			vhtfm.NameError,
			vhtfm.get_doc(doctype="Page", page_name="DocType", module="Core").insert,
		)

	@unittest.skipUnless(
		os.access(vhtfm.get_app_path("vhtfm"), os.W_OK), "Only run if vhtfm app paths is writable"
	)
	@patch.dict(vhtfm.conf, {"developer_mode": 1})
	def test_trashing(self):
		page = vhtfm.new_doc("Page", page_name=vhtfm.generate_hash(), module="Core").insert()

		page.delete()
		vhtfm.db.commit()

		module_path = vhtfm.get_module_path(page.module)
		dir_path = os.path.join(module_path, "page", vhtfm.scrub(page.name))

		self.assertFalse(os.path.exists(dir_path))
