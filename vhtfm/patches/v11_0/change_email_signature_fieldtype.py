# Copyright (c) 2018, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import vhtfm


def execute():
	signatures = vhtfm.db.get_list("User", {"email_signature": ["!=", ""]}, ["name", "email_signature"])
	vhtfm.reload_doc("core", "doctype", "user")
	for d in signatures:
		signature = d.get("email_signature")
		signature = signature.replace("\n", "<br>")
		signature = "<div>" + signature + "</div>"
		vhtfm.db.set_value("User", d.get("name"), "email_signature", signature)
