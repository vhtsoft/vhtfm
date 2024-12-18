import vhtfm


def execute():
	"""
	Rename the Marketing Campaign table to UTM Campaign table
	"""
	if vhtfm.db.exists("DocType", "UTM Campaign"):
		return

	if not vhtfm.db.exists("DocType", "Marketing Campaign"):
		return

	vhtfm.rename_doc("DocType", "Marketing Campaign", "UTM Campaign", force=True)
	vhtfm.reload_doctype("UTM Campaign", force=True)
