# Copyright (c) 2019, Vhtfm Technologies and contributors
# License: MIT. See LICENSE

# import vhtfm
from vhtfm.model.document import Document


class ReviewLevel(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from vhtfm.types import DF

		level_name: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		review_points: DF.Int
		role: DF.Link
	# end: auto-generated types

	pass
