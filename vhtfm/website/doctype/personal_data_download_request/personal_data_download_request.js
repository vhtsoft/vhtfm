// Copyright (c) 2019, Vhtfm Technologies and contributors
// For license information, please see license.txt

vhtfm.ui.form.on("Personal Data Download Request", {
	onload: function (frm) {
		if (frm.is_new()) {
			frm.doc.user = vhtfm.session.user;
		}
	},
});
