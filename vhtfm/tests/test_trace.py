import unittest
from unittest.mock import MagicMock, patch

import vhtfm
from vhtfm.model.document import Document
from vhtfm.model.trace import TracedDocument, traced_field
from vhtfm.tests import UnitTestCase


def create_mock_meta(doctype):
	mock_meta = MagicMock()
	mock_meta.get_table_fields.return_value = []
	return mock_meta


class TestDocument(Document):
	def __init__(self, *args, **kwargs):
		kwargs["doctype"] = "TestDocument"
		with patch("vhtfm.get_meta", return_value=create_mock_meta("TestDocument")):
			super().__init__(*args, **kwargs)


class TestTracedDocument(TracedDocument):
	def __init__(self, *args, **kwargs):
		kwargs["doctype"] = "TestTracedDocument"
		with patch("vhtfm.get_meta", return_value=create_mock_meta("TestTracedDocument")):
			super().__init__(*args, **kwargs)

	test_field = traced_field("test_field", forbidden_values=["forbidden"])

	def validate_positive(self, value):
		if value <= 0:
			raise ValueError("Value must be positive")

	positive_field = traced_field("positive_field", custom_validation=validate_positive)


class TestTrace(unittest.TestCase):
	def setUp(self):
		self.traced_doc = TestTracedDocument()

	def test_traced_field_get(self):
		self.traced_doc._test_field = "test_value"
		self.assertEqual(self.traced_doc.test_field, "test_value")

	def test_traced_field_set(self):
		self.traced_doc.test_field = "new_value"
		self.assertEqual(self.traced_doc._test_field, "new_value")

	def test_traced_field_forbidden_value(self):
		with self.assertRaises(AssertionError):
			self.traced_doc.test_field = "forbidden"

	def test_traced_field_custom_validation(self):
		self.traced_doc.positive_field = 10
		self.assertEqual(self.traced_doc._positive_field, 10)

		with self.assertRaises(AssertionError):
			self.traced_doc.positive_field = -5

	def test_get_valid_dict(self):
		self.traced_doc.test_field = "valid_value"
		self.traced_doc.positive_field = 15
		valid_dict = self.traced_doc.get_valid_dict()
		self.assertEqual(valid_dict["test_field"], "valid_value")
		self.assertEqual(valid_dict["positive_field"], 15)


class TestTracedFieldContext(UnitTestCase):
	def test_traced_field_context(self):
		doc = TestDocument()

		# Before context
		doc.test_field = "forbidden"
		self.assertEqual(doc.test_field, "forbidden")

		with self.trace_fields(TestDocument, "test_field", forbidden_values=["forbidden"]):
			# Inside context
			with self.assertRaises(AssertionError):
				doc.test_field = "forbidden"

			doc.test_field = "allowed"
			self.assertEqual(doc.test_field, "allowed")

		# After context
		doc.test_field = "forbidden"
		self.assertEqual(doc.test_field, "forbidden")

	def test_traced_field_context_custom_validation(self):
		doc = TestDocument()

		def validate_even(obj, value):
			if value % 2 != 0:
				raise ValueError("Value must be even")

		with self.trace_fields(TestDocument, "number_field", custom_validation=validate_even):
			doc.number_field = 2
			self.assertEqual(doc.number_field, 2)

			with self.assertRaises(AssertionError):
				doc.number_field = 3

		# After context, validation should not apply
		doc.number_field = 3
		self.assertEqual(doc.number_field, 3)

	def test_traced_field_context_not_in_test_mode(self):
		doc = TestDocument()

		# Temporarily set vhtfm.flags.in_test to False
		original_in_test = vhtfm.flags.in_test
		vhtfm.flags.in_test = False

		try:
			with self.trace_fields(TestDocument, test_field={"forbidden_values": ["forbidden"]}):
				with self.assertRaises(vhtfm.exceptions.ValidationError):
					doc.test_field = "forbidden"

				doc.test_field = "allowed"
				self.assertEqual(doc.test_field, "allowed")
		finally:
			# Restore the original in_test flag
			vhtfm.flags.in_test = original_in_test

		# After context
		doc.test_field = "forbidden"
		self.assertEqual(doc.test_field, "forbidden")


if __name__ == "__main__":
	unittest.main()