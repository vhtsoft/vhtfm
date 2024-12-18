# Copyright (c) 2020, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import vhtfm


def execute():
	if vhtfm.db.exists("DocType", "Onboarding"):
		vhtfm.rename_doc("DocType", "Onboarding", "Module Onboarding", ignore_if_exists=True)
