# Copyright (c) 2020, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import vhtfm


def execute():
	vhtfm.reload_doc("Email", "doctype", "Notification")

	notifications = vhtfm.get_all("Notification", {"is_standard": 1}, {"name", "channel"})
	for notification in notifications:
		if not notification.channel:
			vhtfm.db.set_value("Notification", notification.name, "channel", "Email", update_modified=False)
			vhtfm.db.commit()
