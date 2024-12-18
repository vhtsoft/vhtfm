import vhtfm


def execute():
	vhtfm.reload_doc("core", "doctype", "doctype_link")
	vhtfm.reload_doc("core", "doctype", "doctype_action")
	vhtfm.reload_doc("core", "doctype", "doctype")
	vhtfm.model.delete_fields({"DocType": ["hide_heading", "image_view", "read_only_onload"]}, delete=1)

	vhtfm.db.delete("Property Setter", {"property": "read_only_onload"})
