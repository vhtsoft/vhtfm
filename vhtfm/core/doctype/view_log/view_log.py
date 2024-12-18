# Copyright (c) 2018, Vhtfm Technologies and contributors
# License: MIT. See LICENSE

import vhtfm
from vhtfm.model.document import Document


class ViewLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from vhtfm.types import DF

		reference_doctype: DF.Link | None
		reference_name: DF.DynamicLink | None
		viewed_by: DF.Data | None
	# end: auto-generated types

	@staticmethod
	def clear_old_logs(days=180):
		from vhtfm.query_builder import Interval
		from vhtfm.query_builder.functions import Now

		table = vhtfm.qb.DocType("View Log")
		vhtfm.db.delete(table, filters=(table.creation < (Now() - Interval(days=days))))
