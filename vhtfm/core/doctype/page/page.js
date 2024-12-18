// Copyright (c) 2016, Vhtfm Technologies and contributors
// For license information, please see license.txt

vhtfm.ui.form.on("Page", {
	refresh: function (frm) {
		if (!vhtfm.boot.developer_mode && vhtfm.session.user != "Administrator") {
			// make the document read-only
			frm.set_read_only();
		}
		if (!frm.is_new() && !frm.doc.istable) {
			frm.add_custom_button(__("Go to {0} Page", [frm.doc.title || frm.doc.name]), () => {
				vhtfm.set_route(frm.doc.name);
			});
		}
	},
});
