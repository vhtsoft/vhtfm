// Copyright (c) 2017, Vhtfm Technologies and contributors
// For license information, please see license.txt

vhtfm.ui.form.on("Print Style", {
	refresh: function (frm) {
		frm.add_custom_button(__("Print Settings"), () => {
			vhtfm.set_route("Form", "Print Settings");
		});
	},
});
