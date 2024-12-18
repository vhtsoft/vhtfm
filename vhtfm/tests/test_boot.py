import vhtfm
from vhtfm.boot import get_unseen_notes, get_user_pages_or_reports
from vhtfm.desk.doctype.note.note import mark_as_seen
from vhtfm.tests import IntegrationTestCase


class TestBootData(IntegrationTestCase):
	def test_get_unseen_notes(self):
		vhtfm.db.delete("Note")
		vhtfm.db.delete("Note Seen By")
		note = vhtfm.get_doc(
			{
				"doctype": "Note",
				"title": "Test Note",
				"notify_on_login": 1,
				"content": "Test Note 1",
				"public": 1,
			}
		)
		note.insert()

		vhtfm.set_user("test@example.com")
		unseen_notes = [d.title for d in get_unseen_notes()]
		self.assertListEqual(unseen_notes, ["Test Note"])

		mark_as_seen(note.name)
		unseen_notes = [d.title for d in get_unseen_notes()]
		self.assertListEqual(unseen_notes, [])


class TestPermissionQueries(IntegrationTestCase):
	@classmethod
	def setUpClass(cls) -> None:
		cls.enterClassContext(cls.enable_safe_exec())
		return super().setUpClass()

	def test_get_user_pages_or_reports_with_permission_query(self):
		# Create a ToDo custom report with admin user
		vhtfm.set_user("Administrator")
		vhtfm.get_doc(
			{
				"doctype": "Report",
				"ref_doctype": "ToDo",
				"report_name": "Test Admin Report",
				"report_type": "Report Builder",
				"is_standard": "No",
			}
		).insert()

		# Add permission query such that each user can only see their own custom reports
		vhtfm.get_doc(
			doctype="Server Script",
			name="test_report_permission_query",
			script_type="Permission Query",
			reference_doctype="Report",
			script="""conditions = f"(`tabReport`.is_standard = 'Yes' or `tabReport`.owner = '{vhtfm.session.user}')"
				""",
		).insert()

		# Create a ToDo custom report with test user
		vhtfm.set_user("test@example.com")
		vhtfm.get_doc(
			{
				"doctype": "Report",
				"ref_doctype": "ToDo",
				"report_name": "Test User Report",
				"report_type": "Report Builder",
				"is_standard": "No",
			}
		).insert(ignore_permissions=True)

		get_user_pages_or_reports("Report")
		allowed_reports = vhtfm.cache.get_value("has_role:Report", user=vhtfm.session.user)

		# Test user must not see admin user's report
		self.assertNotIn("Test Admin Report", allowed_reports)
		self.assertIn("Test User Report", allowed_reports)
