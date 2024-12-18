import vhtfm
from vhtfm.utils.install import add_standard_navbar_items


def execute():
	# Add standard navbar items for ERPNext in Navbar Settings
	vhtfm.reload_doc("core", "doctype", "navbar_settings")
	vhtfm.reload_doc("core", "doctype", "navbar_item")
	add_standard_navbar_items()
