// Copyright (c) 2018, Vhtfm Technologies and contributors
// For license information, please see license.txt
vhtfm.provide("vhtfm.auto_repeat");

vhtfm.ui.form.on("Auto Repeat", {
	setup: function (frm) {
		frm.fields_dict["reference_doctype"].get_query = function () {
			return {
				query: "vhtfm.automation.doctype.auto_repeat.auto_repeat.get_auto_repeat_doctypes",
			};
		};

		frm.fields_dict["reference_document"].get_query = function () {
			return {
				filters: {
					auto_repeat: "",
				},
			};
		};

		frm.fields_dict["print_format"].get_query = function () {
			return {
				filters: {
					doc_type: frm.doc.reference_doctype,
				},
			};
		};
	},

	refresh: function (frm) {
		// auto repeat message
		if (frm.is_new()) {
			let customize_form_link = `<a href="/app/customize-form">${__("Customize Form")}</a>`;
			frm.dashboard.set_headline(
				__('To configure Auto Repeat, enable "Allow Auto Repeat" from {0}.', [
					customize_form_link,
				])
			);
		}

		// view document button
		if (!frm.is_dirty()) {
			let label = __("View {0}", [__(frm.doc.reference_doctype)]);
			frm.add_custom_button(label, () =>
				vhtfm.set_route("List", frm.doc.reference_doctype, { auto_repeat: frm.doc.name })
			);
		}

		// auto repeat schedule
		vhtfm.auto_repeat.render_schedule(frm);

		frm.trigger("toggle_submit_on_creation");
	},

	reference_doctype: function (frm) {
		frm.trigger("toggle_submit_on_creation");
	},

	toggle_submit_on_creation: function (frm) {
		// submit on creation checkbox
		if (frm.doc.reference_doctype) {
			vhtfm.model.with_doctype(frm.doc.reference_doctype, () => {
				let meta = vhtfm.get_meta(frm.doc.reference_doctype);
				frm.toggle_display("submit_on_creation", meta.is_submittable);
			});
		}
	},

	template: function (frm) {
		if (frm.doc.template) {
			vhtfm.model.with_doc("Email Template", frm.doc.template, () => {
				let email_template = vhtfm.get_doc("Email Template", frm.doc.template);
				frm.set_value("subject", email_template.subject);
				frm.set_value("message", email_template.response);
				frm.refresh_field("subject");
				frm.refresh_field("message");
			});
		}
	},

	get_contacts: function (frm) {
		frm.call("fetch_linked_contacts");
	},

	preview_message: function (frm) {
		if (frm.doc.message) {
			vhtfm.call({
				method: "vhtfm.automation.doctype.auto_repeat.auto_repeat.generate_message_preview",
				args: {
					reference_dt: frm.doc.reference_doctype,
					reference_doc: frm.doc.reference_document,
					subject: frm.doc.subject,
					message: frm.doc.message,
				},
				callback: function (r) {
					if (r.message) {
						vhtfm.msgprint(r.message.message, r.message.subject);
					}
				},
			});
		} else {
			vhtfm.msgprint(__("Please setup a message first"), __("Message not setup"));
		}
	},
});

vhtfm.auto_repeat.render_schedule = function (frm) {
	if (!frm.is_dirty() && frm.doc.status !== "Disabled") {
		frm.call("get_auto_repeat_schedule").then((r) => {
			frm.dashboard.reset();
			frm.dashboard.add_section(
				vhtfm.render_template("auto_repeat_schedule", {
					schedule_details: r.message || [],
				}),
				__("Auto Repeat Schedule")
			);
			frm.dashboard.show();
		});
	} else {
		frm.dashboard.hide();
	}
};
