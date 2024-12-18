# Copyright (c) 2015, Vhtfm Technologies and Contributors
# License: MIT. See LICENSE
import vhtfm
from vhtfm.contacts.doctype.address_template.address_template import get_default_address_template
from vhtfm.tests import IntegrationTestCase, UnitTestCase
from vhtfm.utils.jinja import validate_template


class UnitTestAddressTemplate(UnitTestCase):
	"""
	Unit tests for AddressTemplate.
	Use this class for testing individual functions and methods.
	"""

	pass


class TestAddressTemplate(IntegrationTestCase):
	def setUp(self) -> None:
		vhtfm.db.delete("Address Template", {"country": "India"})
		vhtfm.db.delete("Address Template", {"country": "Brazil"})

	def test_default_address_template(self):
		validate_template(get_default_address_template())

	def test_default_is_unset(self):
		vhtfm.get_doc({"doctype": "Address Template", "country": "India", "is_default": 1}).insert()

		self.assertEqual(vhtfm.db.get_value("Address Template", "India", "is_default"), 1)

		vhtfm.get_doc({"doctype": "Address Template", "country": "Brazil", "is_default": 1}).insert()

		self.assertEqual(vhtfm.db.get_value("Address Template", "India", "is_default"), 0)
		self.assertEqual(vhtfm.db.get_value("Address Template", "Brazil", "is_default"), 1)

	def test_delete_address_template(self):
		india = vhtfm.get_doc({"doctype": "Address Template", "country": "India", "is_default": 0}).insert()

		brazil = vhtfm.get_doc(
			{"doctype": "Address Template", "country": "Brazil", "is_default": 1}
		).insert()

		india.reload()  # might have been modified by the second template
		india.delete()  # should not raise an error

		self.assertRaises(vhtfm.ValidationError, brazil.delete)
