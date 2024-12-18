// Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

vhtfm.provide("vhtfm.pages");
vhtfm.provide("vhtfm.views");

vhtfm.views.Factory = class Factory {
	constructor(opts) {
		$.extend(this, opts);
	}

	show() {
		this.route = vhtfm.get_route();
		this.page_name = vhtfm.get_route_str();

		if (this.before_show && this.before_show() === false) return;

		if (vhtfm.pages[this.page_name]) {
			vhtfm.container.change_to(this.page_name);
			if (this.on_show) {
				this.on_show();
			}
		} else {
			if (this.route[1]) {
				this.make(this.route);
			} else {
				vhtfm.show_not_found(this.route);
			}
		}
	}

	make_page(double_column, page_name, sidebar_postition) {
		return vhtfm.make_page(double_column, page_name, sidebar_postition);
	}
};

vhtfm.make_page = function (double_column, page_name, sidebar_position) {
	if (!page_name) {
		page_name = vhtfm.get_route_str();
	}

	const page = vhtfm.container.add_page(page_name);

	vhtfm.ui.make_app_page({
		parent: page,
		single_column: !double_column,
		sidebar_position: sidebar_position,
	});

	vhtfm.container.change_to(page_name);
	return page;
};
