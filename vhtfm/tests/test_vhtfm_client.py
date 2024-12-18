# Copyright (c) 2022, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import base64

import requests

import vhtfm
from vhtfm.core.doctype.user.user import generate_keys
from vhtfm.vhtfmclient import VhtfmClient, VhtfmException
from vhtfm.model import default_fields
from vhtfm.tests import IntegrationTestCase
from vhtfm.utils.data import get_url


class TestVhtfmClient(IntegrationTestCase):
	PASSWORD = vhtfm.conf.admin_password or "admin"

	def test_insert_many(self):
		server = VhtfmClient(get_url(), "Administrator", self.PASSWORD, verify=False)
		server.insert_many(
			[
				{"doctype": "Note", "title": "Sing"},
				{"doctype": "Note", "title": "a"},
				{"doctype": "Note", "title": "song"},
				{"doctype": "Note", "title": "of"},
				{"doctype": "Note", "title": "sixpence"},
			]
		)
		records = server.get_list("Note", fields=["title"])
		records = [r.get("title") for r in records]

		self.assertIn("Sing", records)
		self.assertIn("a", records)
		self.assertIn("song", records)
		self.assertIn("of", records)
		self.assertIn("sixpence", records)

	def test_create_doc(self):
		server = VhtfmClient(get_url(), "Administrator", self.PASSWORD, verify=False)
		response = server.insert({"doctype": "Note", "title": "test_create"})

		for field in default_fields:
			self.assertIn(field, response)

		self.assertEqual(response.get("doctype"), "Note")
		self.assertEqual(response.get("title"), "test_create")

	def test_list_docs(self):
		server = VhtfmClient(get_url(), "Administrator", self.PASSWORD, verify=False)
		doc_list = server.get_list("Note")

		self.assertTrue(len(doc_list))

	def test_get_doc(self):
		USER = "Administrator"
		TITLE = "get_this"
		DOCTYPE = "Note"
		server = VhtfmClient(get_url(), "Administrator", self.PASSWORD, verify=False)

		NAME = server.insert({"doctype": DOCTYPE, "title": TITLE}).get("name")
		doc = server.get_doc(DOCTYPE, NAME)

		for field in default_fields:
			self.assertIn(field, doc)

		self.assertEqual(doc.get("doctype"), DOCTYPE)
		self.assertEqual(doc.get("name"), NAME)
		self.assertEqual(doc.get("title"), TITLE)
		self.assertEqual(doc.get("owner"), USER)

	def test_get_value_by_filters(self):
		CONTENT = "test get value"
		server = VhtfmClient(get_url(), "Administrator", self.PASSWORD, verify=False)
		server.insert({"doctype": "Note", "title": "get_value", "content": CONTENT}).get("name")

		self.assertEqual(server.get_value("Note", "content", {"title": "get_value"}).get("content"), CONTENT)

	def test_get_value_by_name(self):
		server = VhtfmClient(get_url(), "Administrator", self.PASSWORD, verify=False)
		CONTENT = "test get value"
		NAME = server.insert({"doctype": "Note", "title": "get_value", "content": CONTENT}).get("name")

		self.assertEqual(server.get_value("Note", "content", NAME).get("content"), CONTENT)

	def test_get_value_with_malicious_query(self):
		server = VhtfmClient(get_url(), "Administrator", self.PASSWORD, verify=False)
		server.insert({"doctype": "Note", "title": "get_value"})

		self.assertRaises(
			VhtfmException,
			server.get_value,
			"Note",
			"(select (password) from(__Auth) order by name desc limit 1)",
			{"title": "get_value"},
		)

	def test_get_single(self):
		server = VhtfmClient(get_url(), "Administrator", self.PASSWORD, verify=False)
		server.set_value("Website Settings", "Website Settings", "title_prefix", "test-prefix")
		self.assertEqual(
			server.get_value("Website Settings", "title_prefix", "Website Settings").get("title_prefix"),
			"test-prefix",
		)
		self.assertEqual(
			server.get_value("Website Settings", "title_prefix").get("title_prefix"), "test-prefix"
		)
		vhtfm.db.set_single_value("Website Settings", "title_prefix", "")

	def test_update_doc(self):
		server = VhtfmClient(get_url(), "Administrator", self.PASSWORD, verify=False)
		resp = server.insert({"doctype": "Note", "title": "Sing"})
		doc = server.get_doc("Note", resp.get("name"))

		CONTENT = "<h1>Hello, World!</h1>"
		doc["content"] = CONTENT
		doc = server.update(doc)
		self.assertTrue(doc["content"] == CONTENT)

	def test_update_child_doc(self):
		server = VhtfmClient(get_url(), "Administrator", self.PASSWORD, verify=False)
		vhtfm.db.delete("Contact", {"first_name": "George", "last_name": "Steevens"})
		vhtfm.db.delete("Contact", {"first_name": "William", "last_name": "Shakespeare"})
		vhtfm.db.delete("Communication", {"reference_doctype": "Event"})
		vhtfm.db.delete("Communication Link", {"link_doctype": "Contact"})
		vhtfm.db.delete("Event", {"subject": "Sing a song of sixpence"})
		vhtfm.db.delete("Event Participants", {"reference_doctype": "Contact"})
		vhtfm.db.commit()

		# create multiple contacts
		server.insert_many(
			[
				{"doctype": "Contact", "first_name": "George", "last_name": "Steevens"},
				{"doctype": "Contact", "first_name": "William", "last_name": "Shakespeare"},
			]
		)

		# create an event with one of the created contacts
		event = server.insert(
			{
				"doctype": "Event",
				"subject": "Sing a song of sixpence",
				"event_participants": [
					{"reference_doctype": "Contact", "reference_docname": "George Steevens"}
				],
			}
		)

		# update the event's contact to the second contact
		server.update(
			{
				"doctype": "Event Participants",
				"name": event.get("event_participants")[0].get("name"),
				"reference_docname": "William Shakespeare",
			}
		)

		# the change should run the parent document's validations and
		# create a Communication record with the new contact
		self.assertTrue(vhtfm.db.exists("Communication Link", {"link_name": "William Shakespeare"}))

	def test_delete_doc(self):
		server = VhtfmClient(get_url(), "Administrator", self.PASSWORD, verify=False)
		NAME_TO_DELETE = server.insert({"doctype": "Note", "title": "Sing"}).get("name")
		server.delete("Note", NAME_TO_DELETE)
		self.assertFalse(vhtfm.db.get_value("Note", NAME_TO_DELETE))

	def test_auth_via_api_key_secret(self):
		# generate API key and API secret for administrator
		keys = generate_keys("Administrator")
		vhtfm.db.commit()
		generated_secret = vhtfm.utils.password.get_decrypted_password(
			"User", "Administrator", fieldname="api_secret"
		)

		api_key = vhtfm.db.get_value("User", "Administrator", "api_key")
		header = {"Authorization": f"token {api_key}:{generated_secret}"}
		res = requests.post(get_url() + "/api/method/vhtfm.auth.get_logged_user", headers=header)

		self.assertEqual(res.status_code, 200)
		self.assertEqual("Administrator", res.json()["message"])
		self.assertEqual(keys["api_secret"], generated_secret)

		header = {
			"Authorization": "Basic {}".format(
				base64.b64encode(vhtfm.safe_encode(f"{api_key}:{generated_secret}")).decode()
			)
		}
		res = requests.post(get_url() + "/api/method/vhtfm.auth.get_logged_user", headers=header)
		self.assertEqual(res.status_code, 200)
		self.assertEqual("Administrator", res.json()["message"])

		# Valid api key, invalid api secret
		api_secret = "ksk&93nxoe3os"
		header = {"Authorization": f"token {api_key}:{api_secret}"}
		res = requests.post(get_url() + "/api/method/vhtfm.auth.get_logged_user", headers=header)
		self.assertEqual(res.status_code, 401)

		# random api key and api secret
		api_key = "@3djdk3kld"
		api_secret = "ksk&93nxoe3os"
		header = {"Authorization": f"token {api_key}:{api_secret}"}
		res = requests.post(get_url() + "/api/method/vhtfm.auth.get_logged_user", headers=header)
		self.assertEqual(res.status_code, 401)
