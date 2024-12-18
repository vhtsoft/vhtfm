import vhtfm
from vhtfm.model.rename_doc import rename_doc


def execute():
	if vhtfm.db.table_exists("Email Alert Recipient") and not vhtfm.db.table_exists(
		"Notification Recipient"
	):
		rename_doc("DocType", "Email Alert Recipient", "Notification Recipient")
		vhtfm.reload_doc("email", "doctype", "notification_recipient")

	if vhtfm.db.table_exists("Email Alert") and not vhtfm.db.table_exists("Notification"):
		rename_doc("DocType", "Email Alert", "Notification")
		vhtfm.reload_doc("email", "doctype", "notification")
