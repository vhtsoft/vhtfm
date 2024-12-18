import vhtfm
from vhtfm import format
from vhtfm.tests import IntegrationTestCase


class TestFormatter(IntegrationTestCase):
	def test_currency_formatting(self):
		df = vhtfm._dict({"fieldname": "amount", "fieldtype": "Currency", "options": "currency"})

		doc = vhtfm._dict({"amount": 5})
		vhtfm.db.set_default("currency", "INR")

		# if currency field is not passed then default currency should be used.
		self.assertEqual(format(100000, df, doc, format="#,###.##"), "₹ 100,000.00")

		doc.currency = "USD"
		self.assertEqual(format(100000, df, doc, format="#,###.##"), "$ 100,000.00")

		vhtfm.db.set_default("currency", None)
