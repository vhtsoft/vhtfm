# Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import vhtfm


def execute():
	vhtfm.reload_doc("core", "doctype", "system_settings")
	vhtfm.db.set_single_value("System Settings", "allow_login_after_fail", 60)
