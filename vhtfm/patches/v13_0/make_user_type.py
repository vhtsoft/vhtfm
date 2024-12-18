import vhtfm
from vhtfm.utils.install import create_user_type


def execute():
	vhtfm.reload_doc("core", "doctype", "role")
	vhtfm.reload_doc("core", "doctype", "user_document_type")
	vhtfm.reload_doc("core", "doctype", "user_type_module")
	vhtfm.reload_doc("core", "doctype", "user_select_document_type")
	vhtfm.reload_doc("core", "doctype", "user_type")

	create_user_type()
