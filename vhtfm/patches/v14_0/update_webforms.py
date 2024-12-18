# Copyright (c) 2021, Vhtfm Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt


import vhtfm


def execute():
	vhtfm.reload_doc("website", "doctype", "web_form_list_column")
	vhtfm.reload_doctype("Web Form")

	for web_form in vhtfm.get_all("Web Form", fields=["*"]):
		if web_form.allow_multiple and not web_form.show_list:
			vhtfm.db.set_value("Web Form", web_form.name, "show_list", True)
