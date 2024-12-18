// Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

vhtfm.provide("vhtfm.views.formview");

vhtfm.views.FormFactory = class FormFactory extends vhtfm.views.Factory {
	make(route) {
		var doctype = route[1],
			doctype_layout = vhtfm.router.doctype_layout || doctype;

		if (!vhtfm.views.formview[doctype_layout]) {
			vhtfm.model.with_doctype(doctype, () => {
				this.page = vhtfm.container.add_page(doctype_layout);
				vhtfm.views.formview[doctype_layout] = this.page;
				this.make_and_show(doctype, route);
			});
		} else {
			this.show_doc(route);
		}

		this.setup_events();
	}

	make_and_show(doctype, route) {
		if (vhtfm.router.doctype_layout) {
			vhtfm.model.with_doc("DocType Layout", vhtfm.router.doctype_layout, () => {
				this.make_form(doctype);
				this.show_doc(route);
			});
		} else {
			this.make_form(doctype);
			this.show_doc(route);
		}
	}

	make_form(doctype) {
		this.page.frm = new vhtfm.ui.form.Form(
			doctype,
			this.page,
			true,
			vhtfm.router.doctype_layout
		);
	}

	setup_events() {
		if (!this.initialized) {
			$(document).on("page-change", function () {
				vhtfm.ui.form.close_grid_form();
			});
		}
		this.initialized = true;
	}

	show_doc(route) {
		var doctype = route[1],
			doctype_layout = vhtfm.router.doctype_layout || doctype,
			name = route.slice(2).join("/");

		if (vhtfm.model.new_names[name]) {
			// document has been renamed, reroute
			name = vhtfm.model.new_names[name];
			vhtfm.set_route("Form", doctype_layout, name);
			return;
		}

		const doc = vhtfm.get_doc(doctype, name);
		if (
			doc &&
			vhtfm.model.get_docinfo(doctype, name) &&
			(doc.__islocal || vhtfm.model.is_fresh(doc))
		) {
			// is document available and recent?
			this.render(doctype_layout, name);
		} else {
			this.fetch_and_render(doctype, name, doctype_layout);
		}
	}

	fetch_and_render(doctype, name, doctype_layout) {
		vhtfm.model.with_doc(doctype, name, (name, r) => {
			if (r && r["403"]) return; // not permitted

			if (!(locals[doctype] && locals[doctype][name])) {
				if (name && name.substr(0, 3) === "new") {
					this.render_new_doc(doctype, name, doctype_layout);
				} else {
					vhtfm.show_not_found();
				}
				return;
			}
			this.render(doctype_layout, name);
		});
	}

	render_new_doc(doctype, name, doctype_layout) {
		const new_name = vhtfm.model.make_new_doc_and_get_name(doctype, true);
		if (new_name === name) {
			this.render(doctype_layout, name);
		} else {
			vhtfm.route_flags.replace_route = true;
			vhtfm.set_route("Form", doctype_layout, new_name);
		}
	}

	render(doctype_layout, name) {
		vhtfm.container.change_to(doctype_layout);
		vhtfm.views.formview[doctype_layout].frm.refresh(name);
	}
};
