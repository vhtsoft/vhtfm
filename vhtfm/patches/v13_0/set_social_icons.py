import vhtfm


def execute():
	providers = vhtfm.get_all("Social Login Key")

	for provider in providers:
		doc = vhtfm.get_doc("Social Login Key", provider)
		doc.set_icon()
		doc.save()
