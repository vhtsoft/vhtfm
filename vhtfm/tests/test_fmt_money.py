# Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import vhtfm
from vhtfm.tests import IntegrationTestCase
from vhtfm.utils import fmt_money


class TestFmtMoney(IntegrationTestCase):
	def test_standard(self):
		vhtfm.db.set_default("number_format", "#,###.##")
		self.assertEqual(fmt_money(100), "100.00")
		self.assertEqual(fmt_money(1000), "1,000.00")
		self.assertEqual(fmt_money(10000), "10,000.00")
		self.assertEqual(fmt_money(100000), "100,000.00")
		self.assertEqual(fmt_money(1000000), "1,000,000.00")
		self.assertEqual(fmt_money(10000000), "10,000,000.00")
		self.assertEqual(fmt_money(100000000), "100,000,000.00")
		self.assertEqual(fmt_money(1000000000), "1,000,000,000.00")

	def test_negative(self):
		vhtfm.db.set_default("number_format", "#,###.##")
		self.assertEqual(fmt_money(-100), "-100.00")
		self.assertEqual(fmt_money(-1000), "-1,000.00")
		self.assertEqual(fmt_money(-10000), "-10,000.00")
		self.assertEqual(fmt_money(-100000), "-100,000.00")
		self.assertEqual(fmt_money(-1000000), "-1,000,000.00")
		self.assertEqual(fmt_money(-10000000), "-10,000,000.00")
		self.assertEqual(fmt_money(-100000000), "-100,000,000.00")
		self.assertEqual(fmt_money(-1000000000), "-1,000,000,000.00")

	def test_decimal(self):
		vhtfm.db.set_default("number_format", "#.###,##")
		self.assertEqual(fmt_money(-100), "-100,00")
		self.assertEqual(fmt_money(-1000), "-1.000,00")
		self.assertEqual(fmt_money(-10000), "-10.000,00")
		self.assertEqual(fmt_money(-100000), "-100.000,00")
		self.assertEqual(fmt_money(-1000000), "-1.000.000,00")
		self.assertEqual(fmt_money(-10000000), "-10.000.000,00")
		self.assertEqual(fmt_money(-100000000), "-100.000.000,00")
		self.assertEqual(fmt_money(-1000000000), "-1.000.000.000,00")

	def test_lacs(self):
		vhtfm.db.set_default("number_format", "#,##,###.##")
		self.assertEqual(fmt_money(100), "100.00")
		self.assertEqual(fmt_money(1000), "1,000.00")
		self.assertEqual(fmt_money(10000), "10,000.00")
		self.assertEqual(fmt_money(100000), "1,00,000.00")
		self.assertEqual(fmt_money(1000000), "10,00,000.00")
		self.assertEqual(fmt_money(10000000), "1,00,00,000.00")
		self.assertEqual(fmt_money(100000000), "10,00,00,000.00")
		self.assertEqual(fmt_money(1000000000), "1,00,00,00,000.00")

	def test_no_precision(self):
		vhtfm.db.set_default("number_format", "#,###")
		self.assertEqual(fmt_money(0.3), "0")
		self.assertEqual(fmt_money(100.3), "100")
		self.assertEqual(fmt_money(1000.3), "1,000")
		self.assertEqual(fmt_money(10000.3), "10,000")
		self.assertEqual(fmt_money(-0.3), "0")
		self.assertEqual(fmt_money(-100.3), "-100")
		self.assertEqual(fmt_money(-1000.3), "-1,000")

	def test_currency_precision(self):
		vhtfm.db.set_default("currency_precision", "4")
		vhtfm.db.set_default("number_format", "#,###.##")
		self.assertEqual(fmt_money(100), "100.00")
		self.assertEqual(fmt_money(1000), "1,000.00")
		self.assertEqual(fmt_money(10000), "10,000.00")
		self.assertEqual(fmt_money(100000), "100,000.00")
		self.assertEqual(fmt_money(1000000), "1,000,000.00")
		self.assertEqual(fmt_money(10000000), "10,000,000.00")
		self.assertEqual(fmt_money(100000000), "100,000,000.00")
		self.assertEqual(fmt_money(1000000000), "1,000,000,000.00")
		self.assertEqual(fmt_money(100.23), "100.23")
		self.assertEqual(fmt_money(1000.456), "1,000.456")
		self.assertEqual(fmt_money(10000.7890), "10,000.789")
		self.assertEqual(fmt_money(100000.1234), "100,000.1234")
		self.assertEqual(fmt_money(1000000.3456), "1,000,000.3456")
		self.assertEqual(fmt_money(10000000.3344567), "10,000,000.3345")
		self.assertEqual(fmt_money(100000000.37827268), "100,000,000.3783")
		self.assertEqual(fmt_money(1000000000.2718272637), "1,000,000,000.2718")
		vhtfm.db.set_default("currency_precision", "")

	def test_currency_precision_de_format(self):
		vhtfm.db.set_default("currency_precision", "4")
		vhtfm.db.set_default("number_format", "#.###,##")
		self.assertEqual(fmt_money(100), "100,00")
		self.assertEqual(fmt_money(1000), "1.000,00")
		self.assertEqual(fmt_money(10000), "10.000,00")
		self.assertEqual(fmt_money(100000), "100.000,00")
		self.assertEqual(fmt_money(100.23), "100,23")
		self.assertEqual(fmt_money(1000.456), "1.000,456")
		vhtfm.db.set_default("currency_precision", "")

	def test_custom_fmt_money_format(self):
		self.assertEqual(fmt_money(100000, format="#,###.##"), "100,000.00")
		self.assertEqual(fmt_money(None, format="#,###.##"), "0.00")

	def test_fmt_with_symbol_pos(self):
		vhtfm.db.set_value("Currency", "JPY", "symbol_on_right", 1)
		self.assertEqual(fmt_money(100.0, format="#,###.##", currency="JPY"), "100.00 ¥")
		self.assertEqual(fmt_money(100.0, format="#,###.##", currency="USD"), "$ 100.00")
