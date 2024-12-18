vhtfm.pages["backups"].on_page_load = function (wrapper) {
	var page = vhtfm.ui.make_app_page({
		parent: wrapper,
		title: __("Download Backups"),
		single_column: true,
	});

	page.add_inner_button(__("Set Number of Backups"), function () {
		vhtfm.set_route("Form", "System Settings");
	});

	page.add_inner_button(__("Download Files Backup"), function () {
		vhtfm.call({
			method: "vhtfm.desk.page.backups.backups.schedule_files_backup",
			args: { user_email: vhtfm.session.user_email },
		});
	});

	page.add_inner_button(__("Get Backup Encryption Key"), function () {
		if (vhtfm.user.has_role("System Manager")) {
			vhtfm.verify_password(function () {
				vhtfm.call({
					method: "vhtfm.utils.backups.get_backup_encryption_key",
					callback: function (r) {
						vhtfm.msgprint({
							title: __("Backup Encryption Key"),
							message: __(r.message),
							indicator: "blue",
						});
					},
				});
			});
		} else {
			vhtfm.msgprint({
				title: __("Error"),
				message: __("System Manager privileges required."),
				indicator: "red",
			});
		}
	});

	vhtfm.breadcrumbs.add("Setup");

	$(vhtfm.render_template("backups")).appendTo(page.body.addClass("no-border"));
};
