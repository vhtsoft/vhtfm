import vhtfm


def execute():
	vhtfm.reload_doctype("System Settings")
	# setting first_day_of_the_week value as "Monday" to avoid breaking change
	# because before the configuration was introduced, system used to consider "Monday" as start of the week
	vhtfm.db.set_single_value("System Settings", "first_day_of_the_week", "Monday")
