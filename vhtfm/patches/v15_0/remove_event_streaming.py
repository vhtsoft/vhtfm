import vhtfm


def execute():
	if "event_streaming" in vhtfm.get_installed_apps():
		return

	vhtfm.delete_doc_if_exists("Module Def", "Event Streaming", force=True)

	for doc in [
		"Event Consumer Document Type",
		"Document Type Mapping",
		"Event Producer",
		"Event Producer Last Update",
		"Event Producer Document Type",
		"Event Consumer",
		"Document Type Field Mapping",
		"Event Update Log",
		"Event Update Log Consumer",
		"Event Sync Log",
	]:
		vhtfm.delete_doc_if_exists("DocType", doc, force=True)
