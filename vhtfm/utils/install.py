# Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import getpass

import vhtfm
from vhtfm.geo.doctype.country.country import import_country_and_currency
from vhtfm.utils import cint
from vhtfm.utils.password import update_password


def before_install():
	vhtfm.reload_doc("core", "doctype", "doctype_state")
	vhtfm.reload_doc("core", "doctype", "docfield")
	vhtfm.reload_doc("core", "doctype", "docperm")
	vhtfm.reload_doc("core", "doctype", "doctype_action")
	vhtfm.reload_doc("core", "doctype", "doctype_link")
	vhtfm.reload_doc("desk", "doctype", "form_tour_step")
	vhtfm.reload_doc("desk", "doctype", "form_tour")
	vhtfm.reload_doc("core", "doctype", "doctype")
	vhtfm.clear_cache()


def after_install():
	create_user_type()
	install_basic_docs()

	from vhtfm.core.doctype.file.utils import make_home_folder
	from vhtfm.core.doctype.language.language import sync_languages

	make_home_folder()
	import_country_and_currency()
	sync_languages()

	# save default print setting
	print_settings = vhtfm.get_doc("Print Settings")
	print_settings.save()

	# all roles to admin
	vhtfm.get_doc("User", "Administrator").add_roles(*vhtfm.get_all("Role", pluck="name"))

	# update admin password
	update_password("Administrator", get_admin_password())

	if not vhtfm.conf.skip_setup_wizard:
		# only set home_page if the value doesn't exist in the db
		if not vhtfm.db.get_default("desktop:home_page"):
			vhtfm.db.set_default("desktop:home_page", "setup-wizard")
			vhtfm.db.set_single_value("System Settings", "setup_complete", 0)

	# clear test log
	from vhtfm.tests.utils.generators import _after_install_clear_test_log

	_after_install_clear_test_log()

	add_standard_navbar_items()

	vhtfm.db.commit()


def create_user_type():
	for user_type in ["System User", "Website User"]:
		if not vhtfm.db.exists("User Type", user_type):
			vhtfm.get_doc({"doctype": "User Type", "name": user_type, "is_standard": 1}).insert(
				ignore_permissions=True
			)


def install_basic_docs():
	# core users / roles
	install_docs = [
		{
			"doctype": "User",
			"name": "Administrator",
			"first_name": "Administrator",
			"email": "admin@example.com",
			"enabled": 1,
			"is_admin": 1,
			"roles": [{"role": "Administrator"}],
			"thread_notify": 0,
			"send_me_a_copy": 0,
		},
		{
			"doctype": "User",
			"name": "Guest",
			"first_name": "Guest",
			"email": "guest@example.com",
			"enabled": 1,
			"is_guest": 1,
			"roles": [{"role": "Guest"}],
			"thread_notify": 0,
			"send_me_a_copy": 0,
		},
		{"doctype": "Role", "role_name": "Report Manager"},
		{"doctype": "Role", "role_name": "Translator"},
		{
			"doctype": "Workflow State",
			"workflow_state_name": "Pending",
			"icon": "question-sign",
			"style": "",
		},
		{
			"doctype": "Workflow State",
			"workflow_state_name": "Approved",
			"icon": "ok-sign",
			"style": "Success",
		},
		{
			"doctype": "Workflow State",
			"workflow_state_name": "Rejected",
			"icon": "remove",
			"style": "Danger",
		},
		{"doctype": "Workflow Action Master", "workflow_action_name": "Approve"},
		{"doctype": "Workflow Action Master", "workflow_action_name": "Reject"},
		{"doctype": "Workflow Action Master", "workflow_action_name": "Review"},
		{
			"doctype": "Email Domain",
			"domain_name": "example.com",
			"email_id": "account@example.com",
			"password": "pass",
			"email_server": "imap.example.com",
			"use_imap": 1,
			"smtp_server": "smtp.example.com",
		},
		{
			"doctype": "Email Account",
			"domain": "example.com",
			"email_id": "notifications@example.com",
			"default_outgoing": 1,
		},
		{
			"doctype": "Email Account",
			"domain": "example.com",
			"email_id": "replies@example.com",
			"default_incoming": 1,
		},
	]

	for d in install_docs:
		try:
			vhtfm.get_doc(d).insert(ignore_if_duplicate=True)
		except vhtfm.NameError:
			pass


def get_admin_password():
	return vhtfm.conf.get("admin_password") or getpass.getpass("Set Administrator password: ")


def before_tests():
	if len(vhtfm.get_installed_apps()) > 1:
		# don't run before tests if any other app is installed
		return

	vhtfm.db.truncate("Custom Field")
	vhtfm.db.truncate("Event")

	vhtfm.clear_cache()

	# complete setup if missing
	if not cint(vhtfm.db.get_single_value("System Settings", "setup_complete")):
		complete_setup_wizard()

	vhtfm.db.set_single_value("Website Settings", "disable_signup", 0)
	vhtfm.db.commit()
	vhtfm.clear_cache()


def complete_setup_wizard():
	from vhtfm.desk.page.setup_wizard.setup_wizard import setup_complete

	setup_complete(
		{
			"language": "English",
			"email": "test@vhterp.com",
			"full_name": "Test User",
			"password": "test",
			"country": "United States",
			"timezone": "America/New_York",
			"currency": "USD",
			"enable_telemtry": 1,
		}
	)


def add_standard_navbar_items():
	navbar_settings = vhtfm.get_single("Navbar Settings")

	# don't add settings/help options if they're already present
	if navbar_settings.settings_dropdown and navbar_settings.help_dropdown:
		return

	navbar_settings.settings_dropdown = []
	navbar_settings.help_dropdown = []

	for item in vhtfm.get_hooks("standard_navbar_items"):
		navbar_settings.append("settings_dropdown", item)

	for item in vhtfm.get_hooks("standard_help_items"):
		navbar_settings.append("help_dropdown", item)

	navbar_settings.save()
