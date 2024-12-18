# Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import vhtfm
from vhtfm import _

no_cache = 1


def get_context(context):
	if vhtfm.flags.in_migrate:
		return

	allow_traceback = vhtfm.get_system_settings("allow_error_traceback") if vhtfm.db else False
	if vhtfm.local.flags.disable_traceback and not vhtfm.local.dev_server:
		allow_traceback = False

	if not context.title:
		context.title = _("Server Error")
	if not context.message:
		context.message = _("There was an error building this page")

	return {
		"error": vhtfm.get_traceback().replace("<", "&lt;").replace(">", "&gt;") if allow_traceback else ""
	}
