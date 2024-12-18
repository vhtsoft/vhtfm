# Copyright (c) 2022, Vhtfm and Contributors
# License: MIT. See LICENSE


import vhtfm
from vhtfm.model import data_field_options


def execute():
	custom_field = vhtfm.qb.DocType("Custom Field")
	(
		vhtfm.qb.update(custom_field)
		.set(custom_field.options, None)
		.where((custom_field.fieldtype == "Data") & (custom_field.options.notin(data_field_options)))
	).run()
