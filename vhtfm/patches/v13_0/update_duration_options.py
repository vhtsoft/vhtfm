# Copyright (c) 2020, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import vhtfm


def execute():
	vhtfm.reload_doc("core", "doctype", "DocField")

	if vhtfm.db.has_column("DocField", "show_days"):
		vhtfm.db.sql(
			"""
			UPDATE
				tabDocField
			SET
				hide_days = 1 WHERE show_days = 0
		"""
		)
		vhtfm.db.sql_ddl("alter table tabDocField drop column show_days")

	if vhtfm.db.has_column("DocField", "show_seconds"):
		vhtfm.db.sql(
			"""
			UPDATE
				tabDocField
			SET
				hide_seconds = 1 WHERE show_seconds = 0
		"""
		)
		vhtfm.db.sql_ddl("alter table tabDocField drop column show_seconds")

	vhtfm.clear_cache(doctype="DocField")
