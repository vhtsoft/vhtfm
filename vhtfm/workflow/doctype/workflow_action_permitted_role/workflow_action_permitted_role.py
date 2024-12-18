# Copyright (c) 2022, Vhtfm Technologies and contributors
# For license information, please see license.txt

# import vhtfm
from vhtfm.model.document import Document


class WorkflowActionPermittedRole(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from vhtfm.types import DF

		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		role: DF.Link | None
	# end: auto-generated types

	pass
