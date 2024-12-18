# Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors

from unittest.mock import patch

import vhtfm
from vhtfm.tests import IntegrationTestCase
from vhtfm.utils import get_site_url


class TestClient(IntegrationTestCase):
	def test_set_value(self):
		todo = vhtfm.get_doc(doctype="ToDo", description="test").insert()
		vhtfm.set_value("ToDo", todo.name, "description", "test 1")
		self.assertEqual(vhtfm.get_value("ToDo", todo.name, "description"), "test 1")

		vhtfm.set_value("ToDo", todo.name, {"description": "test 2"})
		self.assertEqual(vhtfm.get_value("ToDo", todo.name, "description"), "test 2")

	def test_delete(self):
		from vhtfm.client import delete
		from vhtfm.desk.doctype.note.note import Note

		note = vhtfm.get_doc(
			doctype="Note",
			title=vhtfm.generate_hash(length=8),
			content="test",
			seen_by=[{"user": "Administrator"}],
		).insert()

		child_row_name = note.seen_by[0].name

		with patch.object(Note, "save") as save:
			delete("Note Seen By", child_row_name)
			save.assert_called()

		delete("Note", note.name)

		self.assertFalse(vhtfm.db.exists("Note", note.name))
		self.assertRaises(vhtfm.DoesNotExistError, delete, "Note", note.name)
		self.assertRaises(vhtfm.DoesNotExistError, delete, "Note Seen By", child_row_name)

	def test_http_valid_method_access(self):
		from vhtfm.client import delete
		from vhtfm.handler import execute_cmd

		vhtfm.set_user("Administrator")

		vhtfm.local.request = vhtfm._dict()
		vhtfm.local.request.method = "POST"

		vhtfm.local.form_dict = vhtfm._dict(
			{"doc": dict(doctype="ToDo", description="Valid http method"), "cmd": "vhtfm.client.save"}
		)
		todo = execute_cmd("vhtfm.client.save")

		self.assertEqual(todo.get("description"), "Valid http method")

		delete("ToDo", todo.name)

	def test_http_invalid_method_access(self):
		from vhtfm.handler import execute_cmd

		vhtfm.set_user("Administrator")

		vhtfm.local.request = vhtfm._dict()
		vhtfm.local.request.method = "GET"

		vhtfm.local.form_dict = vhtfm._dict(
			{"doc": dict(doctype="ToDo", description="Invalid http method"), "cmd": "vhtfm.client.save"}
		)

		self.assertRaises(vhtfm.PermissionError, execute_cmd, "vhtfm.client.save")

	def test_run_doc_method(self):
		from vhtfm.handler import execute_cmd

		if not vhtfm.db.exists("Report", "Test Run Doc Method"):
			report = vhtfm.get_doc(
				{
					"doctype": "Report",
					"ref_doctype": "User",
					"report_name": "Test Run Doc Method",
					"report_type": "Query Report",
					"is_standard": "No",
					"roles": [{"role": "System Manager"}],
				}
			).insert()
		else:
			report = vhtfm.get_doc("Report", "Test Run Doc Method")

		vhtfm.local.request = vhtfm._dict()
		vhtfm.local.request.method = "GET"

		# Whitelisted, works as expected
		vhtfm.local.form_dict = vhtfm._dict(
			{
				"dt": report.doctype,
				"dn": report.name,
				"method": "toggle_disable",
				"cmd": "run_doc_method",
				"args": 0,
			}
		)

		execute_cmd(vhtfm.local.form_dict.cmd)

		# Not whitelisted, throws permission error
		vhtfm.local.form_dict = vhtfm._dict(
			{
				"dt": report.doctype,
				"dn": report.name,
				"method": "create_report_py",
				"cmd": "run_doc_method",
				"args": 0,
			}
		)

		self.assertRaises(vhtfm.PermissionError, execute_cmd, vhtfm.local.form_dict.cmd)

	def test_array_values_in_request_args(self):
		import requests

		from vhtfm.auth import CookieManager, LoginManager

		vhtfm.utils.set_request(path="/")
		vhtfm.local.cookie_manager = CookieManager()
		vhtfm.local.login_manager = LoginManager()
		vhtfm.local.login_manager.login_as("Administrator")
		params = {
			"doctype": "DocType",
			"fields": ["name", "modified"],
			"sid": vhtfm.session.sid,
		}
		headers = {
			"accept": "application/json",
			"content-type": "application/json",
		}
		url = get_site_url(vhtfm.local.site)
		url += "/api/method/vhtfm.client.get_list"

		res = requests.post(url, json=params, headers=headers)
		self.assertEqual(res.status_code, 200)
		data = res.json()
		first_item = data["message"][0]
		self.assertTrue("name" in first_item)
		self.assertTrue("modified" in first_item)

	def test_client_get(self):
		from vhtfm.client import get

		todo = vhtfm.get_doc(doctype="ToDo", description="test").insert()
		filters = {"name": todo.name}
		filters_json = vhtfm.as_json(filters)

		self.assertEqual(get("ToDo", filters=filters).description, "test")
		self.assertEqual(get("ToDo", filters=filters_json).description, "test")
		self.assertEqual(get("System Settings", "", "").doctype, "System Settings")
		self.assertEqual(get("ToDo", filters={}), get("ToDo", filters="{}"))
		todo.delete()

	def test_client_insert(self):
		from vhtfm.client import insert

		def get_random_title():
			return f"test-{vhtfm.generate_hash()}"

		# test insert dict
		doc = {"doctype": "Note", "title": get_random_title(), "content": "test"}
		note1 = insert(doc)
		self.assertTrue(note1)

		# test insert json
		doc["title"] = get_random_title()
		json_doc = vhtfm.as_json(doc)
		note2 = insert(json_doc)
		self.assertTrue(note2)

		# test insert child doc without parent fields
		child_doc = {"doctype": "Note Seen By", "user": "Administrator"}
		with self.assertRaises(vhtfm.ValidationError):
			insert(child_doc)

		# test insert child doc with parent fields
		child_doc = {
			"doctype": "Note Seen By",
			"user": "Administrator",
			"parenttype": "Note",
			"parent": note1.name,
			"parentfield": "seen_by",
		}
		note3 = insert(child_doc)
		self.assertTrue(note3)

		# cleanup
		vhtfm.delete_doc("Note", note1.name)
		vhtfm.delete_doc("Note", note2.name)

	def test_client_insert_many(self):
		from vhtfm.client import insert, insert_many

		def get_random_title():
			return f"test-{vhtfm.generate_hash(length=5)}"

		# insert a (parent) doc
		note1 = {"doctype": "Note", "title": get_random_title(), "content": "test"}
		note1 = insert(note1)

		doc_list = [
			{
				"doctype": "Note Seen By",
				"user": "Administrator",
				"parenttype": "Note",
				"parent": note1.name,
				"parentfield": "seen_by",
			},
			{
				"doctype": "Note Seen By",
				"user": "Administrator",
				"parenttype": "Note",
				"parent": note1.name,
				"parentfield": "seen_by",
			},
			{
				"doctype": "Note Seen By",
				"user": "Administrator",
				"parenttype": "Note",
				"parent": note1.name,
				"parentfield": "seen_by",
			},
			{"doctype": "Note", "title": "not-a-random-title", "content": "test"},
			{"doctype": "Note", "title": get_random_title(), "content": "test"},
			{"doctype": "Note", "title": get_random_title(), "content": "test"},
			{"doctype": "Note", "title": "another-note-title", "content": "test"},
		]

		# insert all docs
		docs = insert_many(doc_list)

		self.assertEqual(len(docs), 7)
		self.assertEqual(vhtfm.db.get_value("Note", docs[3], "title"), "not-a-random-title")
		self.assertEqual(vhtfm.db.get_value("Note", docs[6], "title"), "another-note-title")
		self.assertIn(note1.name, docs)

		# cleanup
		for doc in docs:
			vhtfm.delete_doc("Note", doc)
