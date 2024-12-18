# Copyright (c) 2023, Vhtfm Technologies and Contributors
# See LICENSE

import time

import vhtfm
from vhtfm.core.doctype.doctype.test_doctype import new_doctype
from vhtfm.desk.doctype.bulk_update.bulk_update import submit_cancel_or_update_docs
from vhtfm.tests import IntegrationTestCase, UnitTestCase, timeout


class UnitTestBulkUpdate(UnitTestCase):
	"""
	Unit tests for BulkUpdate.
	Use this class for testing individual functions and methods.
	"""

	pass


class TestBulkUpdate(IntegrationTestCase):
	@classmethod
	def setUpClass(cls) -> None:
		super().setUpClass()
		cls.doctype = new_doctype(is_submittable=1, custom=1).insert().name
		vhtfm.db.commit()
		for _ in range(50):
			vhtfm.new_doc(cls.doctype, some_fieldname=vhtfm.mock("name")).insert()

	@timeout()
	def wait_for_assertion(self, assertion):
		"""Wait till an assertion becomes True"""
		while True:
			if assertion():
				break
			time.sleep(0.2)

	def test_bulk_submit_in_background(self):
		unsubmitted = vhtfm.get_all(self.doctype, {"docstatus": 0}, limit=5, pluck="name")
		failed = submit_cancel_or_update_docs(self.doctype, unsubmitted, action="submit")
		self.assertEqual(failed, [])

		def check_docstatus(docs, status):
			vhtfm.db.rollback()
			matching_docs = vhtfm.get_all(
				self.doctype, {"docstatus": status, "name": ("in", docs)}, pluck="name"
			)
			return set(matching_docs) == set(docs)

		unsubmitted = vhtfm.get_all(self.doctype, {"docstatus": 0}, limit=20, pluck="name")
		submit_cancel_or_update_docs(self.doctype, unsubmitted, action="submit")

		self.wait_for_assertion(lambda: check_docstatus(unsubmitted, 1))

		submitted = vhtfm.get_all(self.doctype, {"docstatus": 1}, limit=20, pluck="name")
		submit_cancel_or_update_docs(self.doctype, submitted, action="cancel")
		self.wait_for_assertion(lambda: check_docstatus(submitted, 2))
