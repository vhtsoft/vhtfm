import Widget from "./base_widget.js";

vhtfm.provide("vhtfm.utils");

export default class QuickListWidget extends Widget {
	constructor(opts) {
		opts.shadow = true;
		super(opts);
	}

	get_config() {
		return {
			document_type: this.document_type,
			label: this.label,
			quick_list_filter: this.quick_list_filter,
		};
	}

	set_actions() {
		if (this.in_customize_mode) return;

		if (vhtfm.model.can_create(this.document_type)) {
			this.setup_add_new_button();
		}
		this.setup_refresh_list_button();
		this.setup_filter_list_button();
	}

	setup_add_new_button() {
		this.add_new_button = $(
			`<div class="add-new btn btn-xs pull-right"
			title="${__("Add New")} ${__(this.document_type)}
			">
				${vhtfm.utils.icon("add", "sm")}
			</div>`
		);

		this.add_new_button.appendTo(this.action_area);
		this.add_new_button.on("click", () => {
			vhtfm.set_route(
				vhtfm.utils.generate_route({
					type: "doctype",
					name: this.document_type,
					doc_view: "New",
				})
			);
		});
	}

	setup_refresh_list_button() {
		this.refresh_list = $(
			`<div class="refresh-list btn btn-xs pull-right" title="${__("Refresh List")}">
				${vhtfm.utils.icon("es-line-reload", "sm")}
			</div>`
		);

		this.refresh_list.appendTo(this.action_area);
		this.refresh_list.on("click", () => {
			this.body.empty();
			this.set_body();
		});
	}

	setup_filter_list_button() {
		this.filter_list = $(
			`<div class="filter-list btn btn-xs pull-right" title="${__("Add/Update Filter")}">
				${vhtfm.utils.icon("filter", "sm")}
			</div>`
		);

		this.filter_list.appendTo(this.action_area);
		this.filter_list.on("click", () => this.setup_filter_dialog());
	}

	setup_filter(doctype) {
		if (this.filter_group) {
			this.filter_group.wrapper.empty();
			delete this.filter_group;
		}

		this.filters = vhtfm.utils.process_filter_expression(this.quick_list_filter);

		this.filter_group = new vhtfm.ui.FilterGroup({
			parent: this.dialog.get_field("filter_area").$wrapper,
			doctype: doctype,
			on_change: () => {},
		});

		vhtfm.model.with_doctype(doctype, () => {
			this.filter_group.add_filters_to_filter_group(this.filters);
			this.dialog.set_df_property("filter_area", "hidden", false);
		});
	}

	setup_filter_dialog() {
		let fields = [
			{
				fieldtype: "HTML",
				fieldname: "filter_area",
			},
		];
		let me = this;
		this.dialog = new vhtfm.ui.Dialog({
			title: __("Set Filters for {0}", [__(this.document_type)]),
			fields: fields,
			primary_action: function () {
				let old_filter = me.quick_list_filter;
				let filters = me.filter_group.get_filters();
				me.quick_list_filter = JSON.stringify(filters);

				this.hide();

				if (old_filter != me.quick_list_filter) {
					me.body.empty();
					me.set_footer();
					me.set_body();
				}
			},
			primary_action_label: __("Save"),
		});

		this.dialog.show();
		this.setup_filter(this.document_type);
	}

	render_loading_state() {
		this.body.empty();
		this.loading = $(`<div class="list-loading-state text-muted">${__("Loading...")}</div>`);
		this.loading.appendTo(this.body);
	}

	render_no_data_state() {
		this.loading = $(`<div class="list-no-data-state text-muted">${__("No Data...")}</div>`);
		this.loading.appendTo(this.body);
	}

	setup_quick_list_item(doc) {
		const indicator = vhtfm.get_indicator(doc, this.document_type);

		let $quick_list_item = $(`
			<div class="quick-list-item">
				<div class="ellipsis left">
					<div class="ellipsis title"
						title="${strip_html(doc[this.title_field_name])}">
						${strip_html(doc[this.title_field_name])}
					</div>
					<div class="timestamp text-muted">
						${vhtfm.datetime.prettyDate(doc.modified)}
					</div>
				</div>
			</div>
		`);

		if (indicator) {
			$(`
				<div class="status indicator-pill ${indicator[1]} ellipsis">
					${__(indicator[0])}
				</div>
			`).appendTo($quick_list_item);
		}

		$(`<div class="right-arrow">${vhtfm.utils.icon("right", "xs")}</div>`).appendTo(
			$quick_list_item
		);

		$quick_list_item.click((e) => {
			if (e.ctrlKey || e.metaKey) {
				vhtfm.open_in_new_tab = true;
			}
			vhtfm.set_route(`${vhtfm.utils.get_form_link(this.document_type, doc.name)}`);
		});

		return $quick_list_item;
	}

	set_body() {
		this.widget.addClass("quick-list-widget-box");

		this.render_loading_state();

		vhtfm.model.with_doctype(this.document_type, () => {
			let fields = ["name"];

			// get name of title field
			if (!this.title_field_name) {
				let meta = vhtfm.get_meta(this.document_type);
				this.title_field_name = (meta && meta.title_field) || "name";
			}

			if (this.title_field_name && this.title_field_name != "name") {
				fields.push(this.title_field_name);
			}

			// check doctype has status field
			this.has_status_field = vhtfm.meta.has_field(this.document_type, "status");

			if (this.has_status_field) {
				fields.push("status");
				fields.push("docstatus");
			}
			// add workflow state field if workflow exist & is active
			let workflow_fieldname = vhtfm.workflow.get_state_fieldname(this.document_type);
			workflow_fieldname && fields.push(workflow_fieldname);
			fields.push("modified");

			let add_fields = vhtfm.listview_settings?.[this.document_type]?.add_fields;
			if (Array.isArray(add_fields)) {
				for (const fieldname of add_fields) {
					// Only keep fields that exist and are permitted
					if (vhtfm.meta.has_field(this.document_type, fieldname)) {
						fields.push(fieldname);
					}
				}
				fields = [...new Set(fields)]; // Remove duplicates
			}

			let quick_list_filter = vhtfm.utils.process_filter_expression(this.quick_list_filter);

			let args = {
				method: "vhtfm.desk.reportview.get",
				args: {
					doctype: this.document_type,
					fields: fields,
					filters: quick_list_filter,
					order_by: "creation desc",
					start: 0,
					page_length: 4,
				},
			};

			vhtfm.call(args).then((r) => {
				if (!r.message) return;
				let data = r.message;

				this.body.empty();
				data = !Array.isArray(data) ? vhtfm.utils.dict(data.keys, data.values) : data;

				if (!data.length) {
					this.render_no_data_state();
					return;
				}

				this.quick_list = data.map((doc) => this.setup_quick_list_item(doc));
				this.quick_list.forEach(($quick_list_item) =>
					$quick_list_item.appendTo(this.body)
				);
			});
		});
	}

	set_footer() {
		this.footer.empty();

		let filters = vhtfm.utils.get_filter_from_json(this.quick_list_filter);
		let route = vhtfm.utils.generate_route({ type: "doctype", name: this.document_type });
		this.see_all_button = $(`
			<div class="see-all btn btn-xs">${__("View List")}</div>
		`).appendTo(this.footer);

		this.see_all_button.click((e) => {
			if (e.ctrlKey || e.metaKey) {
				vhtfm.open_in_new_tab = true;
			}
			if (filters) {
				vhtfm.route_options = filters;
			}
			vhtfm.set_route(route);
		});
	}
}
