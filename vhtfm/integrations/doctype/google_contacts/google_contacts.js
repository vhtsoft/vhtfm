// Copyright (c) 2019, Vhtfm Technologies and contributors
// For license information, please see license.txt

vhtfm.ui.form.on("Google Contacts", {
	refresh: function (frm) {
		if (!frm.doc.enable) {
			frm.dashboard.set_headline(
				__("To use Google Contacts, enable {0}.", [
					`<a href='/app/google-settings'>${__("Google Settings")}</a>`,
				])
			);
		}

		vhtfm.realtime.on("import_google_contacts", (data) => {
			if (data.progress) {
				frm.dashboard.show_progress(
					"Import Google Contacts",
					(data.progress / data.total) * 100,
					__("Importing {0} of {1}", [data.progress, data.total])
				);
				if (data.progress === data.total) {
					frm.dashboard.hide_progress("Import Google Contacts");
				}
			}
		});

		if (frm.doc.refresh_token) {
			let sync_button = frm.add_custom_button(__("Sync Contacts"), function () {
				vhtfm.show_alert({
					indicator: "green",
					message: __("Syncing"),
				});
				vhtfm
					.call({
						method: "vhtfm.integrations.doctype.google_contacts.google_contacts.sync",
						args: {
							g_contact: frm.doc.name,
						},
						btn: sync_button,
					})
					.then((r) => {
						vhtfm.hide_progress();
						vhtfm.msgprint(r.message);
					});
			});
		}
	},
	authorize_google_contacts_access: function (frm) {
		vhtfm.call({
			method: "vhtfm.integrations.doctype.google_contacts.google_contacts.authorize_access",
			args: {
				g_contact: frm.doc.name,
				reauthorize: frm.doc.authorization_code ? 1 : 0,
			},
			callback: function (r) {
				if (!r.exc) {
					frm.save();
					window.open(r.message.url);
				}
			},
		});
	},
});
