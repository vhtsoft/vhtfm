import vhtfm


def execute():
	singles = vhtfm.qb.Table("tabSingles")
	vhtfm.qb.from_(singles).delete().where(
		(singles.doctype == "System Settings") & (singles.field == "is_first_startup")
	).run()
