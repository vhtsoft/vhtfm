# Copyright (c) 2020, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import vhtfm


def execute():
	vhtfm.reload_doc("website", "doctype", "web_page_block")
	# remove unused templates
	vhtfm.delete_doc("Web Template", "Navbar with Links on Right", force=1)
	vhtfm.delete_doc("Web Template", "Footer Horizontal", force=1)
