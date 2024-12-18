# Copyright (c) 2020, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import vhtfm


def execute():
	vhtfm.delete_doc("DocType", "Package Publish Tool", ignore_missing=True)
	vhtfm.delete_doc("DocType", "Package Document Type", ignore_missing=True)
	vhtfm.delete_doc("DocType", "Package Publish Target", ignore_missing=True)
