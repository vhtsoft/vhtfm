# Copyright (c) 2019, Vhtfm Technologies and contributors
# License: MIT. See LICENSE

# import vhtfm
from vhtfm.model.document import Document


class WebsiteRouteRedirect(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from vhtfm.types import DF

		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		redirect_http_status: DF.Literal["301", "302", "307", "308"]
		source: DF.SmallText
		target: DF.SmallText
	# end: auto-generated types

	pass
