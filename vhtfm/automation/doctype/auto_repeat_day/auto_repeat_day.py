# Copyright (c) 2020, Vhtfm Technologies and contributors
# License: MIT. See LICENSE

# import vhtfm
from vhtfm.model.document import Document


class AutoRepeatDay(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from vhtfm.types import DF

		day: DF.Literal["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types

	pass
