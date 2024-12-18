import vhtfm


def execute():
	vhtfm.db.delete("DocType", {"name": "Feedback Request"})
