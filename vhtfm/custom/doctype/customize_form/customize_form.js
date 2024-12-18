// Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

vhtfm.provide("vhtfm.customize_form");

vhtfm.ui.form.on("Customize Form", {
	setup: function (frm) {
		// save the last setting if refreshing
		window.addEventListener("beforeunload", () => {
			if (frm.doc.doc_type && frm.doc.doc_type != "undefined") {
				localStorage["customize_doctype"] = frm.doc.doc_type;
			}
		});
	},

	onload: function (frm) {
		frm.set_query("doc_type", function () {
			return {
				filters: [
					["DocType", "issingle", "=", 0],
					["DocType", "custom", "=", 0],
					["DocType", "name", "not in", vhtfm.model.core_doctypes_list],
					["DocType", "restrict_to_domain", "in", vhtfm.boot.active_domains],
				],
			};
		});

		frm.set_query("default_print_format", function () {
			return {
				filters: {
					print_format_type: ["!=", "JS"],
					doc_type: ["=", frm.doc.doc_type],
				},
			};
		});

		$(frm.wrapper).on("grid-row-render", function (e, grid_row) {
			if (grid_row.doc && grid_row.doc.fieldtype == "Section Break") {
				$(grid_row.row).css({ "font-weight": "bold" });
			}

			grid_row.row.removeClass("highlight");

			if (
				grid_row.doc.is_custom_field &&
				!grid_row.row.hasClass("highlight") &&
				!grid_row.doc.is_system_generated
			) {
				grid_row.row.addClass("highlight");
			}
		});
	},

	doc_type: function (frm) {
		if (frm.doc.doc_type) {
			return frm.call({
				method: "fetch_to_customize",
				doc: frm.doc,
				freeze: true,
				callback: function (r) {
					if (r) {
						if (r._server_messages && r._server_messages.length) {
							frm.set_value("doc_type", "");
						} else {
							frm.refresh();
							frm.trigger("add_customize_child_table_button");
							frm.trigger("setup_default_views");
						}
					}
					localStorage["customize_doctype"] = frm.doc.doc_type;
				},
			});
		} else {
			frm.refresh();
		}
	},

	is_calendar_and_gantt: function (frm) {
		frm.trigger("setup_default_views");
	},

	add_customize_child_table_button: function (frm) {
		frm.doc.fields.forEach(function (f) {
			if (!["Table", "Table MultiSelect"].includes(f.fieldtype)) return;

			frm.add_custom_button(
				__(f.options),
				() => frm.set_value("doc_type", f.options),
				__("Customize Child Table")
			);
		});
	},

	refresh: function (frm) {
		frm.disable_save(true);
		frm.page.clear_icons();

		if (frm.doc.doc_type) {
			vhtfm.model.with_doctype(frm.doc.doc_type).then(() => {
				frm.page.set_title(__("Customize Form - {0}", [__(frm.doc.doc_type)]));
				vhtfm.customize_form.set_primary_action(frm);

				frm.add_custom_button(
					__("Go to {0} List", [__(frm.doc.doc_type)]),
					function () {
						vhtfm.set_route("List", frm.doc.doc_type);
					},
					__("Actions")
				);

				frm.add_custom_button(
					__("Set Permissions"),
					function () {
						vhtfm.set_route("permission-manager", frm.doc.doc_type);
					},
					__("Actions")
				);

				frm.add_custom_button(
					__("Reload"),
					function () {
						frm.script_manager.trigger("doc_type");
					},
					__("Actions")
				);

				frm.add_custom_button(
					__("Reset Layout"),
					() => {
						frm.trigger("reset_layout");
					},
					__("Actions")
				);

				frm.add_custom_button(
					__("Reset All Customizations"),
					function () {
						vhtfm.customize_form.confirm(__("Remove all customizations?"), frm);
					},
					__("Actions")
				);

				frm.add_custom_button(
					__("Trim Table"),
					function () {
						frm.trigger("trim_table");
					},
					__("Actions")
				);

				const is_autoname_autoincrement = frm.doc.autoname === "autoincrement";
				frm.set_df_property("naming_rule", "hidden", is_autoname_autoincrement);
				frm.set_df_property("autoname", "read_only", is_autoname_autoincrement);
				frm.toggle_display(
					["queue_in_background"],
					vhtfm.get_meta(frm.doc.doc_type).is_submittable || 0
				);

				render_form_builder(frm);
				frm.get_field("form_builder").tab.set_active();
			});
		}

		frm.events.setup_export(frm);
		frm.events.setup_sort_order(frm);
		frm.events.set_default_doc_type(frm);
	},

	set_default_doc_type(frm) {
		let doc_type;
		if (vhtfm.route_options && vhtfm.route_options.doc_type) {
			doc_type = vhtfm.route_options.doc_type;
			vhtfm.route_options = null;
			localStorage.removeItem("customize_doctype");
		}
		if (!doc_type) {
			doc_type = localStorage.getItem("customize_doctype");
		}
		if (doc_type) {
			setTimeout(() => frm.set_value("doc_type", doc_type, false, true), 1000);
		}
	},

	reset_layout(frm) {
		vhtfm.confirm(
			__("Layout will be reset to standard layout, are you sure you want to do this?"),
			() => {
				return frm.call({
					doc: frm.doc,
					method: "reset_layout",
					callback: function (r) {
						if (!r.exc) {
							vhtfm.show_alert({
								message: __("Layout Reset"),
								indicator: "green",
							});
							vhtfm.customize_form.clear_locals_and_refresh(frm);
						}
					},
				});
			}
		);
	},

	async trim_table(frm) {
		let dropped_columns = await vhtfm.xcall(
			"vhtfm.custom.doctype.customize_form.customize_form.get_orphaned_columns",
			{ doctype: frm.doc.doc_type }
		);

		if (!dropped_columns?.length) {
			vhtfm.toast(__("This doctype has no orphan fields to trim"));
			return;
		}
		let msg = __(
			"Warning: DATA LOSS IMMINENT! Proceeding will permanently delete following database columns from doctype {0}:",
			[frm.doc.doc_type.bold()]
		);
		msg += "<ol>" + dropped_columns.map((col) => `<li>${col}</li>`).join("") + "</ol>";
		msg += __("This action is irreversible. Do you wish to continue?");

		vhtfm.confirm(msg, () => {
			return frm.call({
				doc: frm.doc,
				method: "trim_table",
				callback: function (r) {
					if (!r.exc) {
						vhtfm.show_alert({
							message: __("Table Trimmed"),
							indicator: "green",
						});
						vhtfm.customize_form.clear_locals_and_refresh(frm);
					}
				},
			});
		});
	},

	setup_export(frm) {
		if (vhtfm.boot.developer_mode) {
			frm.add_custom_button(
				__("Export Customizations"),
				function () {
					vhtfm.prompt(
						[
							{
								fieldtype: "Link",
								fieldname: "module",
								options: "Module Def",
								label: __("Module to Export"),
								reqd: 1,
							},
							{
								fieldtype: "Check",
								fieldname: "sync_on_migrate",
								label: __("Sync on Migrate"),
								default: 1,
							},
							{
								fieldtype: "Check",
								fieldname: "with_permissions",
								label: __("Export Custom Permissions"),
								description: __(
									"Exported permissions will be force-synced on every migrate overriding any other customization."
								),
								default: 0,
							},
						],
						function (data) {
							vhtfm.call({
								method: "vhtfm.modules.utils.export_customizations",
								args: {
									doctype: frm.doc.doc_type,
									module: data.module,
									sync_on_migrate: data.sync_on_migrate,
									with_permissions: data.with_permissions,
								},
							});
						},
						__("Select Module")
					);
				},
				__("Actions")
			);
		}
	},

	setup_sort_order(frm) {
		// sort order select
		if (frm.doc.doc_type) {
			var fields = $.map(frm.doc.fields, function (df) {
				return vhtfm.model.is_value_type(df.fieldtype) ? df.fieldname : null;
			});
			fields = ["", "name", "creation", "modified"].concat(fields);
			frm.set_df_property("sort_field", "options", fields);
		}
	},

	setup_default_views(frm) {
		vhtfm.model.set_default_views_for_doctype(frm.doc.doc_type, frm);
	},
});

// can't delete standard fields
vhtfm.ui.form.on("Customize Form Field", {
	before_fields_remove: function (frm, doctype, name) {
		const row = vhtfm.get_doc(doctype, name);

		if (row.is_system_generated) {
			vhtfm.throw(
				__(
					"Cannot delete system generated field <strong>{0}</strong>. You can hide it instead.",
					[__(row.label) || row.fieldname]
				)
			);
		}

		if (!(row.is_custom_field || row.__islocal)) {
			vhtfm.throw(
				__("Cannot delete standard field <strong>{0}</strong>. You can hide it instead.", [
					__(row.label) || row.fieldname,
				])
			);
		}
	},
	fields_add: function (frm, cdt, cdn) {
		var f = vhtfm.model.get_doc(cdt, cdn);
		f.is_system_generated = false;
		f.is_custom_field = true;
		frm.trigger("setup_default_views");
	},

	form_render(frm, doctype, docname) {
		frm.trigger("setup_fetch_from_fields", doctype, docname);
	},
});

let parenttype, parent; // used in the form events for the child tables: links, actions and states

// can't delete standard links
vhtfm.ui.form.on("DocType Link", {
	before_links_remove: function (frm, doctype, name) {
		let row = vhtfm.get_doc(doctype, name);
		parenttype = row.parenttype; // used in the event links_remove
		parent = row.parent; // used in the event links_remove
		if (!(row.custom || row.__islocal)) {
			vhtfm.msgprint(__("Cannot delete standard link. You can hide it if you want"));
			throw "cannot delete standard link";
		}
	},
	links_add: function (frm, cdt, cdn) {
		let f = vhtfm.model.get_doc(cdt, cdn);
		f.custom = 1;
	},
	links_remove: function (frm, doctype, name) {
		// replicate the changed rows from the browser's copy of the parent doc to the current 'Customize Form' doc
		let parent_doc = locals[parenttype][parent];
		frm.doc.links = parent_doc.links;
	},
});

// can't delete standard actions
vhtfm.ui.form.on("DocType Action", {
	before_actions_remove: function (frm, doctype, name) {
		let row = vhtfm.get_doc(doctype, name);
		parenttype = row.parenttype; // used in the event actions_remove
		parent = row.parent; // used in the event actions_remove
		if (!(row.custom || row.__islocal)) {
			vhtfm.msgprint(__("Cannot delete standard action. You can hide it if you want"));
			throw "cannot delete standard action";
		}
	},
	actions_add: function (frm, cdt, cdn) {
		let f = vhtfm.model.get_doc(cdt, cdn);
		f.custom = 1;
	},
	actions_remove: function (frm, doctype, name) {
		// replicate the changed rows from the browser's copy of the parent doc to the current 'Customize Form' doc
		let parent_doc = locals[parenttype][parent];
		frm.doc.actions = parent_doc.actions;
	},
});

// can't delete standard states
vhtfm.ui.form.on("DocType State", {
	before_states_remove: function (frm, doctype, name) {
		let row = vhtfm.get_doc(doctype, name);
		parenttype = row.parenttype; // used in the event states_remove
		parent = row.parent; // used in the event states_remove
		if (!(row.custom || row.__islocal)) {
			vhtfm.msgprint(__("Cannot delete standard document state."));
			throw "cannot delete standard document state";
		}
	},
	states_add: function (frm, cdt, cdn) {
		let f = vhtfm.model.get_doc(cdt, cdn);
		f.custom = 1;
	},
	states_remove: function (frm, doctype, name) {
		// replicate the changed rows from the browser's copy of the parent doc to the current 'Customize Form' doc
		let parent_doc = locals[parenttype][parent];
		frm.doc.states = parent_doc.states;
	},
});

vhtfm.customize_form.save_customization = function (frm) {
	if (frm.doc.doc_type) {
		return frm.call({
			doc: frm.doc,
			freeze: true,
			freeze_message: __("Saving Customization..."),
			btn: frm.page.btn_primary,
			method: "save_customization",
			callback: function (r) {
				if (!r.exc) {
					vhtfm.customize_form.clear_locals_and_refresh(frm);
					frm.script_manager.trigger("doc_type");
				}
			},
		});
	}
};

vhtfm.customize_form.update_fields_from_form_builder = function (frm) {
	let form_builder = vhtfm.form_builder;
	if (form_builder?.store) {
		let fields = form_builder.store.update_fields();

		// if fields is a string, it means there is an error
		if (typeof fields === "string") {
			vhtfm.throw(fields);
		}
		frm.refresh_fields();
	}
};

vhtfm.customize_form.set_primary_action = function (frm) {
	frm.page.set_primary_action(__("Update"), () => {
		this.update_fields_from_form_builder(frm);
		this.save_customization(frm);
	});
};

vhtfm.customize_form.confirm = function (msg, frm) {
	if (!frm.doc.doc_type) return;

	var d = new vhtfm.ui.Dialog({
		title: "Reset To Defaults",
		fields: [
			{
				fieldtype: "HTML",
				options: __("All customizations will be removed. Please confirm."),
			},
		],
		primary_action: function () {
			return frm.call({
				doc: frm.doc,
				method: "reset_to_defaults",
				callback: function (r) {
					if (r.exc) {
						vhtfm.msgprint(r.exc);
					} else {
						d.hide();
						vhtfm.show_alert({
							message: __("Customizations Reset"),
							indicator: "green",
						});
						vhtfm.customize_form.clear_locals_and_refresh(frm);
					}
				},
			});
		},
	});

	vhtfm.customize_form.confirm.dialog = d;
	d.show();
};

vhtfm.customize_form.clear_locals_and_refresh = function (frm) {
	delete frm.doc.__unsaved;
	// clear doctype from locals
	vhtfm.model.clear_doc("DocType", frm.doc.doc_type);
	delete vhtfm.meta.docfield_copy[frm.doc.doc_type];
	frm.refresh();
};

function render_form_builder(frm) {
	if (vhtfm.form_builder && vhtfm.form_builder.doctype === frm.doc.doc_type) {
		vhtfm.form_builder.setup_page_actions();
		vhtfm.form_builder.store.fetch();
		return;
	}

	if (vhtfm.form_builder) {
		vhtfm.form_builder.wrapper = $(frm.fields_dict["form_builder"].wrapper);
		vhtfm.form_builder.frm = frm;
		vhtfm.form_builder.doctype = frm.doc.doc_type;
		vhtfm.form_builder.customize = true;
		vhtfm.form_builder.init(true);
		vhtfm.form_builder.store.fetch();
	} else {
		vhtfm.require("form_builder.bundle.js").then(() => {
			vhtfm.form_builder = new vhtfm.ui.FormBuilder({
				wrapper: $(frm.fields_dict["form_builder"].wrapper),
				frm: frm,
				doctype: frm.doc.doc_type,
				customize: true,
			});
		});
	}
}

extend_cscript(cur_frm.cscript, new vhtfm.model.DocTypeController({ frm: cur_frm }));
