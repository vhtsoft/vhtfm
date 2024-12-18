import vhtfm


def execute():
	doctype = "Integration Request"

	if not vhtfm.db.has_column(doctype, "integration_type"):
		return

	vhtfm.db.set_value(
		doctype,
		{"integration_type": "Remote", "integration_request_service": ("!=", "PayPal")},
		"is_remote_request",
		1,
	)
	vhtfm.db.set_value(
		doctype,
		{"integration_type": "Subscription Notification"},
		"request_description",
		"Subscription Notification",
	)
