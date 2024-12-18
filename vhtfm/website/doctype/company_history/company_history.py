# Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

# License: MIT. See LICENSE

import vhtfm
from vhtfm.model.document import Document


class CompanyHistory(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from vhtfm.types import DF

		highlight: DF.Text | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		year: DF.Data | None
	# end: auto-generated types

	pass
