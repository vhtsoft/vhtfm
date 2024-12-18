import vhtfm


def execute():
	days = vhtfm.db.get_single_value("Website Settings", "auto_account_deletion")
	vhtfm.db.set_single_value("Website Settings", "auto_account_deletion", days * 24)
