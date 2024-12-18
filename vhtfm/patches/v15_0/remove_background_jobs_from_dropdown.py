import vhtfm


def execute():
	item = vhtfm.db.exists("Navbar Item", {"item_label": "Background Jobs"})
	if not item:
		return

	vhtfm.delete_doc("Navbar Item", item)
