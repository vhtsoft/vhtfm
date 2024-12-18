import vhtfm


def execute():
	column = "apply_user_permissions"
	to_remove = ["DocPerm", "Custom DocPerm"]

	for doctype in to_remove:
		if vhtfm.db.table_exists(doctype):
			if column in vhtfm.db.get_table_columns(doctype):
				vhtfm.db.sql(f"alter table `tab{doctype}` drop column {column}")

	vhtfm.reload_doc("core", "doctype", "docperm", force=True)
	vhtfm.reload_doc("core", "doctype", "custom_docperm", force=True)
