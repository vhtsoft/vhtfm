import vhtfm
from vhtfm.desk.page.setup_wizard.install_fixtures import update_global_search_doctypes


def execute():
	vhtfm.reload_doc("desk", "doctype", "global_search_doctype")
	vhtfm.reload_doc("desk", "doctype", "global_search_settings")
	update_global_search_doctypes()
