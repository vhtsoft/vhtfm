import vhtfm


def execute():
	if vhtfm.db.table_exists("Prepared Report"):
		vhtfm.reload_doc("core", "doctype", "prepared_report")
		prepared_reports = vhtfm.get_all("Prepared Report")
		for report in prepared_reports:
			vhtfm.delete_doc("Prepared Report", report.name)
