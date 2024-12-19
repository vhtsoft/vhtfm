# Copyright (c) 2015, Vhtfm Technologies and contributors
# License: MIT. See LICENSE

from vhtfm.model.document import Document


class NoteSeenBy(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from vhtfm.types import DF

		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		user: DF.Link | None
	# end: auto-generated types

	pass