import vhtfm


def execute():
	table = vhtfm.qb.DocType("Report")
	vhtfm.qb.update(table).set(table.prepared_report, 0).where(table.disable_prepared_report == 1)
