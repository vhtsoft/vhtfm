# Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and contributors
# License: MIT. See LICENSE

import vhtfm
from vhtfm import _
from vhtfm.model.document import Document
from vhtfm.utils import cint, get_fullname

exclude_from_linked_with = True


class DocShare(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from vhtfm.types import DF

		everyone: DF.Check
		notify_by_email: DF.Check
		read: DF.Check
		share: DF.Check
		share_doctype: DF.Link
		share_name: DF.DynamicLink
		submit: DF.Check
		user: DF.Link | None
		write: DF.Check
	# end: auto-generated types

	no_feed_on_delete = True

	def validate(self):
		self.validate_user()
		self.check_share_permission()
		self.check_is_submittable()
		self.cascade_permissions_downwards()
		self.get_doc().run_method("validate_share", self)

	def cascade_permissions_downwards(self):
		if self.share or self.write or self.submit:
			self.read = 1
		if self.submit:
			self.write = 1

	def get_doc(self):
		if not getattr(self, "_doc", None):
			self._doc = vhtfm.get_doc(self.share_doctype, self.share_name)
		return self._doc

	def validate_user(self):
		if self.everyone:
			self.user = None
		elif not self.user:
			vhtfm.throw(_("User is mandatory for Share"), vhtfm.MandatoryError)

	def check_share_permission(self):
		if not self.flags.ignore_share_permission and not vhtfm.has_permission(
			self.share_doctype, "share", self.get_doc()
		):
			vhtfm.throw(_('You need to have "Share" permission'), vhtfm.PermissionError)

	def check_is_submittable(self):
		if self.submit and not cint(vhtfm.db.get_value("DocType", self.share_doctype, "is_submittable")):
			vhtfm.throw(
				_("Cannot share {0} with submit permission as the doctype {1} is not submittable").format(
					vhtfm.bold(self.share_name), vhtfm.bold(self.share_doctype)
				)
			)

	def after_insert(self):
		doc = self.get_doc()
		owner = get_fullname(self.owner)

		if self.everyone:
			doc.add_comment("Shared", _("{0} shared this document with everyone").format(owner))
		else:
			doc.add_comment(
				"Shared", _("{0} shared this document with {1}").format(owner, get_fullname(self.user))
			)

	def on_trash(self):
		if not self.flags.ignore_share_permission:
			self.check_share_permission()

		self.get_doc().add_comment(
			"Unshared",
			_("{0} un-shared this document with {1}").format(
				get_fullname(self.owner), get_fullname(self.user)
			),
		)


def on_doctype_update():
	"""Add index in `tabDocShare` for `(user, share_doctype)`"""
	vhtfm.db.add_index("DocShare", ["user", "share_doctype"])
	vhtfm.db.add_index("DocShare", ["share_doctype", "share_name"])