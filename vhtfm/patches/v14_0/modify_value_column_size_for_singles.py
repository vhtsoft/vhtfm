import vhtfm


def execute():
	if vhtfm.db.db_type == "mariadb":
		vhtfm.db.sql_ddl("alter table `tabSingles` modify column `value` longtext")
