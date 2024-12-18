// Copyright (c) 2021, Vhtfm Technologies and contributors
// For license information, please see license.txt

vhtfm.ui.form.on("Package", {
	validate: function (frm) {
		if (!frm.doc.package_name) {
			frm.set_value("package_name", frm.doc.name.toLowerCase().replace(" ", "-"));
		}
	},

	license_type: function (frm) {
		vhtfm
			.call("vhtfm.core.doctype.package.package.get_license_text", {
				license_type: frm.doc.license_type,
			})
			.then((r) => {
				frm.set_value("license", r.message);
			});
	},
});
