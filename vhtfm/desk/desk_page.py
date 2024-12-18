# Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import vhtfm


@vhtfm.whitelist()
def get(name):
	"""
	Return the :term:`doclist` of the `Page` specified by `name`
	"""
	page = vhtfm.get_doc("Page", name)
	if page.is_permitted():
		page.load_assets()
		docs = vhtfm._dict(page.as_dict())
		if getattr(page, "_dynamic_page", None):
			docs["_dynamic_page"] = 1

		return docs
	else:
		vhtfm.response["403"] = 1
		raise vhtfm.PermissionError("No read permission for Page %s" % (page.title or name))


@vhtfm.whitelist(allow_guest=True)
def getpage():
	"""
	Load the page from `vhtfm.form` and send it via `vhtfm.response`
	"""
	page = vhtfm.form_dict.get("name")
	doc = get(page)

	vhtfm.response.docs.append(doc)
