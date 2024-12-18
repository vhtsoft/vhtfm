import vhtfm


def execute():
	doctype = "Top Bar Item"
	if not vhtfm.db.table_exists(doctype) or not vhtfm.db.has_column(doctype, "target"):
		return

	vhtfm.reload_doc("website", "doctype", "top_bar_item")
	vhtfm.db.set_value(doctype, {"target": 'target = "_blank"'}, "open_in_new_tab", 1)
