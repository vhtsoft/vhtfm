import vhtfm
from vhtfm.model.rename_doc import rename_doc


def execute():
	if vhtfm.db.exists("DocType", "Client Script"):
		return

	vhtfm.flags.ignore_route_conflict_validation = True
	rename_doc("DocType", "Custom Script", "Client Script")
	vhtfm.flags.ignore_route_conflict_validation = False

	vhtfm.reload_doctype("Client Script", force=True)
