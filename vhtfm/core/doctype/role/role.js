// Copyright (c) 2022, Vhtfm Technologies Pvt. Ltd. and Contributors
// MIT License. See LICENSE

vhtfm.ui.form.on("Role", {
	refresh: function (frm) {
		if (frm.doc.name === "All") {
			frm.dashboard.add_comment(
				__("Role 'All' will be given to all system + website users."),
				"yellow"
			);
		} else if (frm.doc.name === "Desk User") {
			frm.dashboard.add_comment(
				__("Role 'Desk User' will be given to all system users."),
				"yellow"
			);
		}

		frm.set_df_property("is_custom", "read_only", vhtfm.session.user !== "Administrator");

		frm.add_custom_button("Role Permissions Manager", function () {
			vhtfm.route_options = { role: frm.doc.name };
			vhtfm.set_route("permission-manager");
		});
		frm.add_custom_button("Show Users", function () {
			vhtfm.route_options = { role: frm.doc.name };
			vhtfm.set_route("List", "User", "Report");
		});
	},
});
