import vhtfm


def execute():
	vhtfm.reload_doc("workflow", "doctype", "workflow_transition")
	vhtfm.db.sql("update `tabWorkflow Transition` set allow_self_approval=1")
