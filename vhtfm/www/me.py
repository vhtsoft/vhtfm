# Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import vhtfm
import vhtfm.www.list
from vhtfm import _

no_cache = 1


def get_context(context):
	if vhtfm.session.user == "Guest":
		vhtfm.throw(_("You need to be logged in to access this page"), vhtfm.PermissionError)

	context.current_user = vhtfm.get_doc("User", vhtfm.session.user)
	context.show_sidebar = False
