import vhtfm
from vhtfm.utils import cint


def execute():
	vhtfm.reload_doctype("Dropbox Settings")
	check_dropbox_enabled = cint(vhtfm.db.get_single_value("Dropbox Settings", "enabled"))
	if check_dropbox_enabled == 1:
		vhtfm.db.set_single_value("Dropbox Settings", "file_backup", 1)
