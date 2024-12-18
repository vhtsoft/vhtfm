// Copyright (c) 2020, Vhtfm Technologies and contributors
// For license information, please see license.txt

vhtfm.ui.form.on("Navbar Settings", {
	after_save: function (frm) {
		vhtfm.ui.toolbar.clear_cache();
	},
});
