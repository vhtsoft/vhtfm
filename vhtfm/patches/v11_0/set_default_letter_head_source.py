import vhtfm


def execute():
	vhtfm.reload_doctype("Letter Head")

	# source of all existing letter heads must be HTML
	vhtfm.db.sql("update `tabLetter Head` set source = 'HTML'")
