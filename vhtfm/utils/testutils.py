# Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import vhtfm


def add_custom_field(doctype, fieldname, fieldtype="Data", options=None):
	vhtfm.get_doc(
		{
			"doctype": "Custom Field",
			"dt": doctype,
			"fieldname": fieldname,
			"fieldtype": fieldtype,
			"options": options,
		}
	).insert()


def clear_custom_fields(doctype):
	vhtfm.db.delete("Custom Field", {"dt": doctype})
	vhtfm.clear_cache(doctype=doctype)
