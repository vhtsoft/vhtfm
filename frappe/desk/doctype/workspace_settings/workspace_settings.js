// Copyright (c) 2024, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Workspace Settings", {
	setup(frm) {
		frm.hide_full_form_button = true;
		frm.docfields = [];
		let workspace_visibilty = JSON.parse(frm.doc.workspace_visibility_json || "{}");

		// build fields from workspaces
		for (let w of frappe.boot.allowed_workspaces) {
			if (w.public) {
				frm.docfields.push({
					fieldtype: "Check",
					fieldname: w.name,
					label: w.title,
					initial_value: workspace_visibilty[w.name] !== 0, // not set is also visible
				});
			}
		}

		frappe.temp = frm;
	},
	validate(frm) {
		frm.doc.workspace_visibility_json = JSON.stringify(frm.dialog.get_values());
		frm.doc.workspace_setup_completed = 1;
	},
	after_save(frm) {
		// reload page to show latest sidebar
		window.location.reload();
	},
	refresh(frm) {
		frm.dialog.set_alert(__("Select modules you want to see in the sidebar"));
	},
});
