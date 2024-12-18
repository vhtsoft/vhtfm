vhtfm.pages["print-format-builder-beta"].on_page_load = function (wrapper) {
	vhtfm.ui.make_app_page({
		parent: wrapper,
		title: __("Print Format Builder"),
		single_column: true,
	});

	// hot reload in development
	if (vhtfm.boot.developer_mode) {
		vhtfm.hot_update = vhtfm.hot_update || [];
		vhtfm.hot_update.push(() => load_print_format_builder_beta(wrapper));
	}
};

vhtfm.pages["print-format-builder-beta"].on_page_show = function (wrapper) {
	load_print_format_builder_beta(wrapper);
};

function load_print_format_builder_beta(wrapper) {
	let route = vhtfm.get_route();
	let $parent = $(wrapper).find(".layout-main-section");
	$parent.empty();

	if (route.length > 1) {
		vhtfm.require("print_format_builder.bundle.js").then(() => {
			vhtfm.print_format_builder = new vhtfm.ui.PrintFormatBuilder({
				wrapper: $parent,
				page: wrapper.page,
				print_format: route[1],
			});
		});
	} else {
		let d = new vhtfm.ui.Dialog({
			title: __("Create or Edit Print Format"),
			fields: [
				{
					label: __("Action"),
					fieldname: "action",
					fieldtype: "Select",
					options: [
						{ label: __("Create New"), value: "Create" },
						{ label: __("Edit Existing"), value: "Edit" },
					],
					change() {
						let action = d.get_value("action");
						d.get_primary_btn().text(action === "Create" ? __("Create") : __("Edit"));
					},
				},
				{
					label: __("Select Document Type"),
					fieldname: "doctype",
					fieldtype: "Link",
					options: "DocType",
					filters: {
						istable: 0,
					},
					reqd: 1,
					default: vhtfm.route_options ? vhtfm.route_options.doctype : null,
				},
				{
					label: __("New Print Format Name"),
					fieldname: "print_format_name",
					fieldtype: "Data",
					depends_on: (doc) => doc.action === "Create",
					mandatory_depends_on: (doc) => doc.action === "Create",
				},
				{
					label: __("Select Print Format"),
					fieldname: "print_format",
					fieldtype: "Link",
					options: "Print Format",
					only_select: 1,
					depends_on: (doc) => doc.action === "Edit",
					get_query() {
						return {
							filters: {
								doc_type: d.get_value("doctype"),
								print_format_builder_beta: 1,
							},
						};
					},
					mandatory_depends_on: (doc) => doc.action === "Edit",
				},
			],
			primary_action_label: __("Edit"),
			primary_action({ action, doctype, print_format, print_format_name }) {
				if (action === "Edit") {
					vhtfm.set_route("print-format-builder-beta", print_format);
				} else if (action === "Create") {
					d.get_primary_btn().prop("disabled", true);
					vhtfm.db
						.insert({
							doctype: "Print Format",
							name: print_format_name,
							doc_type: doctype,
							print_format_builder_beta: 1,
						})
						.then((doc) => {
							vhtfm.set_route("print-format-builder-beta", doc.name);
						})
						.finally(() => {
							d.get_primary_btn().prop("disabled", false);
						});
				}
			},
		});
		d.set_value("action", "Create");
		d.show();
	}
}
