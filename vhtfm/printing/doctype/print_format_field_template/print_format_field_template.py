# Copyright (c) 2021, Vhtfm Technologies and contributors
# For license information, please see license.txt

import vhtfm
from vhtfm import _
from vhtfm.model.document import Document


class PrintFormatFieldTemplate(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from vhtfm.types import DF

		document_type: DF.Link
		field: DF.Data | None
		module: DF.Link | None
		standard: DF.Check
		template: DF.Code | None
		template_file: DF.Data | None
	# end: auto-generated types

	def validate(self):
		if self.standard and not vhtfm.conf.developer_mode and not vhtfm.flags.in_patch:
			vhtfm.throw(_("Enable developer mode to create a standard Print Template"))

	def before_insert(self):
		self.validate_duplicate()

	def on_update(self):
		self.validate_duplicate()
		self.export_doc()

	def validate_duplicate(self):
		if not self.standard:
			return
		if not self.field:
			return

		filters = {"document_type": self.document_type, "field": self.field}
		if not self.is_new():
			filters.update({"name": ("!=", self.name)})
		result = vhtfm.get_all("Print Format Field Template", filters=filters, limit=1)
		if result:
			vhtfm.throw(
				_("A template already exists for field {0} of {1}").format(
					vhtfm.bold(self.field), vhtfm.bold(self.document_type)
				),
				vhtfm.DuplicateEntryError,
				title=_("Duplicate Entry"),
			)

	def export_doc(self):
		from vhtfm.modules.utils import export_module_json

		export_module_json(self, self.standard, self.module)
