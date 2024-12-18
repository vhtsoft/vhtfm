# Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import json

import vhtfm
from vhtfm.model.document import Document
from vhtfm.permissions import AUTOMATIC_ROLES
from vhtfm.utils import get_fullname, parse_addr

exclude_from_linked_with = True


class ToDo(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from vhtfm.types import DF

		allocated_to: DF.Link | None
		assigned_by: DF.Link | None
		assigned_by_full_name: DF.ReadOnly | None
		assignment_rule: DF.Link | None
		color: DF.Color | None
		date: DF.Date | None
		description: DF.TextEditor
		priority: DF.Literal["High", "Medium", "Low"]
		reference_name: DF.DynamicLink | None
		reference_type: DF.Link | None
		role: DF.Link | None
		sender: DF.Data | None
		status: DF.Literal["Open", "Closed", "Cancelled"]
	# end: auto-generated types

	DocType = "ToDo"

	def validate(self):
		self._assignment = None
		if self.is_new():
			if self.assigned_by == self.allocated_to:
				assignment_message = vhtfm._("{0} self assigned this task: {1}").format(
					get_fullname(self.assigned_by), self.description
				)
			else:
				assignment_message = vhtfm._("{0} assigned {1}: {2}").format(
					get_fullname(self.assigned_by), get_fullname(self.allocated_to), self.description
				)

			self._assignment = {"text": assignment_message, "comment_type": "Assigned"}

		else:
			# NOTE the previous value is only available in validate method
			if self.get_db_value("status") != self.status:
				if self.allocated_to == vhtfm.session.user:
					removal_message = vhtfm._("{0} removed their assignment.").format(
						get_fullname(vhtfm.session.user)
					)
				else:
					removal_message = vhtfm._("Assignment of {0} removed by {1}").format(
						get_fullname(self.allocated_to), get_fullname(vhtfm.session.user)
					)

				self._assignment = {"text": removal_message, "comment_type": "Assignment Completed"}

	def on_update(self):
		if self._assignment:
			self.add_assign_comment(**self._assignment)

		self.update_in_reference()

	def on_trash(self):
		self.delete_communication_links()
		self.update_in_reference()

	def add_assign_comment(self, text, comment_type):
		if not (self.reference_type and self.reference_name):
			return

		vhtfm.get_doc(self.reference_type, self.reference_name).add_comment(comment_type, text)

	def delete_communication_links(self):
		# unlink todo from linked comments
		return vhtfm.db.delete("Communication Link", {"link_doctype": self.doctype, "link_name": self.name})

	def update_in_reference(self):
		if not (self.reference_type and self.reference_name):
			return

		try:
			assignments = vhtfm.db.get_values(
				"ToDo",
				{
					"reference_type": self.reference_type,
					"reference_name": self.reference_name,
					"status": ("not in", ("Cancelled", "Closed")),
					"allocated_to": ("is", "set"),
				},
				"allocated_to",
				pluck=True,
				for_update=True,
			)
			assignments.reverse()

			if vhtfm.get_meta(self.reference_type).issingle:
				vhtfm.db.set_single_value(
					self.reference_type,
					"_assign",
					json.dumps(assignments) if assignments else "",
					update_modified=False,
				)
			else:
				vhtfm.db.set_value(
					self.reference_type,
					self.reference_name,
					"_assign",
					json.dumps(assignments) if assignments else "",
					update_modified=False,
				)

		except Exception as e:
			if vhtfm.db.is_table_missing(e) and vhtfm.flags.in_install:
				# no table
				return

			elif vhtfm.db.is_missing_column(e):
				from vhtfm.database.schema import add_column

				add_column(self.reference_type, "_assign", "Text")
				self.update_in_reference()

			else:
				raise

	@classmethod
	def get_owners(cls, filters=None):
		"""Return list of owners after applying filters on ToDos."""
		rows = vhtfm.get_all(cls.DocType, filters=filters or {}, fields=["allocated_to"])
		return [parse_addr(row.allocated_to)[1] for row in rows if row.allocated_to]


# NOTE: todo is viewable if a user is an owner, or set as assigned_to value, or has any role that is allowed to access ToDo doctype.
def on_doctype_update():
	vhtfm.db.add_index("ToDo", ["reference_type", "reference_name"])


def get_permission_query_conditions(user):
	if not user:
		user = vhtfm.session.user

	todo_roles = vhtfm.permissions.get_doctype_roles("ToDo")
	todo_roles = set(todo_roles) - set(AUTOMATIC_ROLES)

	if any(check in todo_roles for check in vhtfm.get_roles(user)):
		return None
	else:
		return """(`tabToDo`.allocated_to = {user} or `tabToDo`.assigned_by = {user})""".format(
			user=vhtfm.db.escape(user)
		)


def has_permission(doc, ptype="read", user=None):
	user = user or vhtfm.session.user
	todo_roles = vhtfm.permissions.get_doctype_roles("ToDo", ptype)
	todo_roles = set(todo_roles) - set(AUTOMATIC_ROLES)

	if any(check in todo_roles for check in vhtfm.get_roles(user)):
		return True
	else:
		return doc.allocated_to == user or doc.assigned_by == user


@vhtfm.whitelist()
def new_todo(description):
	vhtfm.get_doc({"doctype": "ToDo", "description": description}).insert()
