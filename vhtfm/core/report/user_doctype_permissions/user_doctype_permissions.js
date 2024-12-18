// Copyright (c) 2024, Vhtfm Technologies and contributors
// For license information, please see license.txt

vhtfm.query_reports["User Doctype Permissions"] = {
	filters: [
		{
			fieldname: "user",
			label: __("User"),
			fieldtype: "Link",
			options: "User",
			reqd: 1,
		},
	],
};
