# Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import vhtfm


def execute():
	vhtfm.reload_doc("core", "doctype", "system_settings", force=1)
	vhtfm.db.set_single_value("System Settings", "password_reset_limit", 3)
