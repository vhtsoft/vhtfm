// Copyright (c) 2022, Vhtfm Technologies and contributors
// For license information, please see license.txt

vhtfm.ui.form.on("RQ Worker", {
	refresh: function (frm) {
		// Nothing in this form is supposed to be editable.
		frm.disable_form();
	},
});
