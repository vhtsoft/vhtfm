import vhtfm


def execute():
	vhtfm.reload_doctype("System Settings")
	doc = vhtfm.get_single("System Settings")
	doc.enable_chat = 1

	# Changes prescribed by Nabin Hait (nabin@vhtfm.io)
	doc.flags.ignore_mandatory = True
	doc.flags.ignore_permissions = True

	doc.save()
