import vhtfm
from vhtfm.model.rename_doc import rename_doc


def execute():
	if vhtfm.db.table_exists("Standard Reply") and not vhtfm.db.table_exists("Email Template"):
		rename_doc("DocType", "Standard Reply", "Email Template")
		vhtfm.reload_doc("email", "doctype", "email_template")
