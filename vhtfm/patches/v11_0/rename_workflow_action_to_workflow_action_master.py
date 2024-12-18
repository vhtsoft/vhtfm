import vhtfm
from vhtfm.model.rename_doc import rename_doc


def execute():
	if vhtfm.db.table_exists("Workflow Action") and not vhtfm.db.table_exists("Workflow Action Master"):
		rename_doc("DocType", "Workflow Action", "Workflow Action Master")
		vhtfm.reload_doc("workflow", "doctype", "workflow_action_master")
