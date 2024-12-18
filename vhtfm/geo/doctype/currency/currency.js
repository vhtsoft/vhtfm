// Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
// License: See license.txt

vhtfm.ui.form.on("Currency", {
	refresh(frm) {
		frm.set_intro("");
		if (!frm.doc.enabled) {
			frm.set_intro(__("This Currency is disabled. Enable to use in transactions"));
		}
	},
});
