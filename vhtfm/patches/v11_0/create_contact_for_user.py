import re

import vhtfm
from vhtfm.core.doctype.user.user import create_contact


def execute():
	"""Create Contact for each User if not present"""
	vhtfm.reload_doc("integrations", "doctype", "google_contacts")
	vhtfm.reload_doc("contacts", "doctype", "contact")
	vhtfm.reload_doc("core", "doctype", "dynamic_link")

	contact_meta = vhtfm.get_meta("Contact")
	if contact_meta.has_field("phone_nos") and contact_meta.has_field("email_ids"):
		vhtfm.reload_doc("contacts", "doctype", "contact_phone")
		vhtfm.reload_doc("contacts", "doctype", "contact_email")

	users = vhtfm.get_all("User", filters={"name": ("not in", "Administrator, Guest")}, fields=["*"])
	for user in users:
		if vhtfm.db.exists("Contact", {"email_id": user.email}) or vhtfm.db.exists(
			"Contact Email", {"email_id": user.email}
		):
			continue
		if user.first_name:
			user.first_name = re.sub("[<>]+", "", vhtfm.safe_decode(user.first_name))
		if user.last_name:
			user.last_name = re.sub("[<>]+", "", vhtfm.safe_decode(user.last_name))
		create_contact(user, ignore_links=True, ignore_mandatory=True)
