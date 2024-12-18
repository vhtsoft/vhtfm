import vhtfm


def execute():
	vhtfm.db.change_column_type("__Auth", column="password", type="TEXT")
