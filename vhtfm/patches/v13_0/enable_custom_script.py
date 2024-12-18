# Copyright (c) 2020, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import vhtfm


def execute():
	"""Enable all the existing Client script"""

	vhtfm.db.sql(
		"""
		UPDATE `tabClient Script` SET enabled=1
	"""
	)
