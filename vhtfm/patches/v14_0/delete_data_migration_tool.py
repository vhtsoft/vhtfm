# Copyright (c) 2022, Vhtfm Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

import vhtfm


def execute():
	doctypes = vhtfm.get_all("DocType", {"module": "Data Migration", "custom": 0}, pluck="name")
	for doctype in doctypes:
		vhtfm.delete_doc("DocType", doctype, ignore_missing=True)

	vhtfm.delete_doc("Module Def", "Data Migration", ignore_missing=True, force=True)
