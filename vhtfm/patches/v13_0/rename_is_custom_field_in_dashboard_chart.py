import vhtfm
from vhtfm.model.utils.rename_field import rename_field


def execute():
	if not vhtfm.db.table_exists("Dashboard Chart"):
		return

	vhtfm.reload_doc("desk", "doctype", "dashboard_chart")

	if vhtfm.db.has_column("Dashboard Chart", "is_custom"):
		rename_field("Dashboard Chart", "is_custom", "use_report_chart")
