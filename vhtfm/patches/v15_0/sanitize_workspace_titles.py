import vhtfm
from vhtfm.desk.doctype.workspace.workspace import update_page
from vhtfm.utils import strip_html
from vhtfm.utils.html_utils import unescape_html


def execute():
	workspaces_to_update = vhtfm.get_all(
		"Workspace",
		filters={"module": ("is", "not set")},
		fields=["name", "title", "icon", "indicator_color", "parent_page as parent", "public"],
	)
	for workspace in workspaces_to_update:
		new_title = strip_html(unescape_html(workspace.title))

		if new_title == workspace.title:
			continue

		workspace.title = new_title
		try:
			update_page(**workspace)
			vhtfm.db.commit()

		except Exception:
			vhtfm.db.rollback()
