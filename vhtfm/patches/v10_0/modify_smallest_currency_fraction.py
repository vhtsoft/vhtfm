# Copyright (c) 2018, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import vhtfm


def execute():
	vhtfm.db.set_value("Currency", "USD", "smallest_currency_fraction_value", "0.01")
