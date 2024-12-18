import vhtfm


def execute():
	categories = vhtfm.get_list("Blog Category")
	for category in categories:
		doc = vhtfm.get_doc("Blog Category", category["name"])
		doc.set_route()
		doc.save()
