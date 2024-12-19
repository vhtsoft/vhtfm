# Copyright (c) 2020, Vhtfm Technologies and contributors
# License: MIT. See LICENSE

from vhtfm.model.document import Document


class ModuleProfile(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from vhtfm.core.doctype.block_module.block_module import BlockModule
		from vhtfm.types import DF

		block_modules: DF.Table[BlockModule]
		module_profile_name: DF.Data
	# end: auto-generated types

	def onload(self):
		from vhtfm.utils.modules import get_modules_from_all_apps

		self.set_onload("all_modules", sorted(m.get("module_name") for m in get_modules_from_all_apps()))

	def get_permission_log_options(self, event=None):
		return {"fields": ["block_modules"]}