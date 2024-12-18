# Copyright (c) 2020, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import vhtfm


def execute():
	"""Set default module for standard Web Template, if none."""
	vhtfm.reload_doc("website", "doctype", "Web Template Field")
	vhtfm.reload_doc("website", "doctype", "web_template")

	standard_templates = vhtfm.get_list("Web Template", {"standard": 1})
	for template in standard_templates:
		doc = vhtfm.get_doc("Web Template", template.name)
		if not doc.module:
			doc.module = "Website"
			doc.save()
