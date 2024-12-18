import vhtfm


def execute():
	for name in ("desktop", "space"):
		vhtfm.delete_doc("Page", name)
