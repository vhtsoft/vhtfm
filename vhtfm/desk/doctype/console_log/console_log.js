// Copyright (c) 2020, Vhtfm Technologies and contributors
// For license information, please see license.txt

vhtfm.ui.form.on("Console Log", {
	refresh: function (frm) {
		frm.add_custom_button(__("Re-Run in Console"), () => {
			window.localStorage.setItem("system_console_code", frm.doc.script);
			window.localStorage.setItem("system_console_type", frm.doc.type);
			vhtfm.set_route("Form", "System Console");
		});
	},
});
