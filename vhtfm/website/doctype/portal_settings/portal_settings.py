# Copyright (c) 2015, Vhtfm Technologies and contributors
# License: MIT. See LICENSE

import vhtfm
from vhtfm.model.document import Document
from vhtfm.website.path_resolver import validate_path


class PortalSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from vhtfm.types import DF
		from vhtfm.website.doctype.portal_menu_item.portal_menu_item import PortalMenuItem

		custom_menu: DF.Table[PortalMenuItem]
		default_portal_home: DF.Data | None
		default_role: DF.Link | None
		hide_standard_menu: DF.Check
		menu: DF.Table[PortalMenuItem]
	# end: auto-generated types

	def add_item(self, item):
		"""insert new portal menu item if route is not set, or role is different"""
		exists = [d for d in self.get("menu", []) if d.get("route") == item.get("route")]
		if exists and item.get("role"):
			if exists[0].role != item.get("role"):
				exists[0].role = item.get("role")
				return True
		elif not exists:
			item["enabled"] = 1
			self.append("menu", item)
			return True

	@vhtfm.whitelist()
	def reset(self):
		"""Restore defaults"""
		self.menu = []
		self.sync_menu()

	def sync_menu(self):
		"""Sync portal menu items"""
		dirty = False
		for item in vhtfm.get_hooks("standard_portal_menu_items"):
			if item.get("role") and not vhtfm.db.exists("Role", item.get("role")):
				vhtfm.get_doc({"doctype": "Role", "role_name": item.get("role"), "desk_access": 0}).insert()
			if self.add_item(item):
				dirty = True

		self.remove_deleted_doctype_items()
		if dirty:
			self.save()

	def on_update(self):
		self.clear_cache()

	def clear_cache(self):
		# make js and css
		# clear web cache (for menus!)
		vhtfm.clear_cache(user="Guest")

		from vhtfm.website.utils import clear_cache

		clear_cache()

		# clears role based home pages
		vhtfm.clear_cache()

	def remove_deleted_doctype_items(self):
		existing_doctypes = set(vhtfm.get_list("DocType", pluck="name"))
		for menu_item in list(self.get("menu") + self.get("custom_menu")):
			if menu_item.reference_doctype not in existing_doctypes:
				self.remove(menu_item)

	def validate(self):
		if vhtfm.request and self.default_portal_home:
			validate_path(self.default_portal_home)
