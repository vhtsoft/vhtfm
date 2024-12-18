# Copyright (c) 2020, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import vhtfm


def execute():
	if not vhtfm.db.table_exists("Data Import"):
		return

	meta = vhtfm.get_meta("Data Import")
	# if Data Import is the new one, return early
	if meta.fields[1].fieldname == "import_type":
		return

	vhtfm.db.sql("DROP TABLE IF EXISTS `tabData Import Legacy`")
	vhtfm.rename_doc("DocType", "Data Import", "Data Import Legacy")
	vhtfm.db.commit()
	vhtfm.db.sql("DROP TABLE IF EXISTS `tabData Import`")
	vhtfm.rename_doc("DocType", "Data Import Beta", "Data Import")
