// Copyright (c) 2019, Vhtfm Technologies and contributors
// For license information, please see license.txt

vhtfm.ui.form.on("Google Settings", {
	refresh: function (frm) {
		frm.dashboard.set_headline(
			__("For more information, {0}.", [
				`<a href='https://erpnext.com/docs/user/manual/en/erpnext_integration/google_settings'>${__(
					"Click here"
				)}</a>`,
			])
		);
	},
});
