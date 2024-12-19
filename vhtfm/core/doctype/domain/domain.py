# Copyright (c) 2017, Vhtfm Technologies and contributors
# License: MIT. See LICENSE

import vhtfm
from vhtfm.custom.doctype.custom_field.custom_field import create_custom_fields
from vhtfm.model.document import Document
from vhtfm.utils import cint


class Domain(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from vhtfm.types import DF

		domain: DF.Data
	# end: auto-generated types

	"""Domain documents are created automatically when DocTypes
	with "Restricted" domains are imported during
	installation or migration"""

	def setup_domain(self):
		"""Setup domain icons, permissions, custom fields etc."""
		self.setup_data()
		self.setup_roles()
		self.setup_properties()
		self.set_values()

		if not cint(vhtfm.defaults.get_defaults().setup_complete):
			# if setup not complete, setup desktop etc.
			self.setup_sidebar_items()
			self.set_default_portal_role()

		if self.data.custom_fields:
			create_custom_fields(self.data.custom_fields)

		if self.data.on_setup:
			# custom on_setup method
			vhtfm.get_attr(self.data.on_setup)()

	def remove_domain(self):
		"""Unset domain settings"""
		self.setup_data()

		if self.data.restricted_roles:
			for role_name in self.data.restricted_roles:
				if vhtfm.db.exists("Role", role_name):
					role = vhtfm.get_doc("Role", role_name)
					role.disabled = 1
					role.save()

		self.remove_custom_field()

	def remove_custom_field(self):
		"""Remove custom_fields when disabling domain"""
		if self.data.custom_fields:
			for doctype in self.data.custom_fields:
				custom_fields = self.data.custom_fields[doctype]

				# custom_fields can be a list or dict
				if isinstance(custom_fields, dict):
					custom_fields = [custom_fields]

				for custom_field_detail in custom_fields:
					custom_field_name = vhtfm.db.get_value(
						"Custom Field", dict(dt=doctype, fieldname=custom_field_detail.get("fieldname"))
					)
					if custom_field_name:
						vhtfm.delete_doc("Custom Field", custom_field_name)

	def setup_roles(self):
		"""Enable roles that are restricted to this domain"""
		if self.data.restricted_roles:
			user = vhtfm.get_doc("User", vhtfm.session.user)
			for role_name in self.data.restricted_roles:
				user.append("roles", {"role": role_name})
				if not vhtfm.db.get_value("Role", role_name):
					vhtfm.get_doc(doctype="Role", role_name=role_name).insert()
					continue

				role = vhtfm.get_doc("Role", role_name)
				role.disabled = 0
				role.save()
			user.save()

	def setup_data(self, domain=None):
		"""Load domain info via hooks"""
		self.data = vhtfm.get_domain_data(self.name)

	def get_domain_data(self, module):
		return vhtfm.get_attr(vhtfm.get_hooks("domains")[self.name] + ".data")

	def set_default_portal_role(self):
		"""Set default portal role based on domain"""
		if self.data.get("default_portal_role"):
			vhtfm.db.set_single_value(
				"Portal Settings", "default_role", self.data.get("default_portal_role")
			)

	def setup_properties(self):
		if self.data.properties:
			for args in self.data.properties:
				vhtfm.make_property_setter(args)

	def set_values(self):
		"""set values based on `data.set_value`"""
		if self.data.set_value:
			for args in self.data.set_value:
				vhtfm.reload_doctype(args[0])
				doc = vhtfm.get_doc(args[0], args[1] or args[0])
				doc.set(args[2], args[3])
				doc.save()

	def setup_sidebar_items(self):
		"""Enable / disable sidebar items"""
		if self.data.allow_sidebar_items:
			# disable all
			vhtfm.db.sql("update `tabPortal Menu Item` set enabled=0")

			# enable
			vhtfm.db.sql(
				"""update `tabPortal Menu Item` set enabled=1
				where route in ({})""".format(", ".join(f'"{d}"' for d in self.data.allow_sidebar_items))
			)

		if self.data.remove_sidebar_items:
			# disable all
			vhtfm.db.sql("update `tabPortal Menu Item` set enabled=1")

			# enable
			vhtfm.db.sql(
				"""update `tabPortal Menu Item` set enabled=0
				where route in ({})""".format(", ".join(f'"{d}"' for d in self.data.remove_sidebar_items))
			)