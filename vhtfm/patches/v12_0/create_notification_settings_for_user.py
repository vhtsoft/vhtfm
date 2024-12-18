import vhtfm
from vhtfm.desk.doctype.notification_settings.notification_settings import (
	create_notification_settings,
)


def execute():
	vhtfm.reload_doc("desk", "doctype", "notification_settings")
	vhtfm.reload_doc("desk", "doctype", "notification_subscribed_document")

	users = vhtfm.get_all("User", fields=["name"])
	for user in users:
		create_notification_settings(user.name)
