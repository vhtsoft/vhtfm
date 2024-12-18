// Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

vhtfm.db = {
	get_list: function (doctype, args) {
		if (!args) {
			args = {};
		}
		args.doctype = doctype;
		if (!args.fields) {
			args.fields = ["name"];
		}
		if (!("limit" in args)) {
			args.limit = 20;
		}
		return new Promise((resolve) => {
			vhtfm.call({
				method: "vhtfm.desk.reportview.get_list",
				args: args,
				type: "GET",
				callback: function (r) {
					resolve(r.message);
				},
			});
		});
	},
	exists: function (doctype, nameOrFilters) {
		return new Promise((resolve) => {
			let filters;
			if (typeof nameOrFilters === "string") {
				// may be cached and more effecient
				vhtfm.db.get_value(doctype, { name: nameOrFilters }, "name").then((r) => {
					r.message && r.message.name ? resolve(true) : resolve(false);
				});
			} else if (typeof nameOrFilters === "object") {
				vhtfm.db.count(doctype, { filters: nameOrFilters, limit: 1 }).then((count) => {
					resolve(count > 0);
				});
			}
		});
	},
	get_value: function (doctype, filters, fieldname, callback, parent_doc) {
		return vhtfm.call({
			method: "vhtfm.client.get_value",
			type: "GET",
			args: {
				doctype: doctype,
				fieldname: fieldname,
				filters: filters,
				parent: parent_doc,
			},
			callback: function (r) {
				callback && callback(r.message);
			},
		});
	},
	get_single_value: (doctype, field) => {
		return new Promise((resolve) => {
			vhtfm
				.call({
					method: "vhtfm.client.get_single_value",
					args: { doctype, field },
					type: "GET",
				})
				.then((r) => resolve(r ? r.message : null));
		});
	},
	set_value: function (doctype, docname, fieldname, value, callback) {
		return vhtfm.call({
			method: "vhtfm.client.set_value",
			args: {
				doctype: doctype,
				name: docname,
				fieldname: fieldname,
				value: value,
			},
			callback: function (r) {
				callback && callback(r.message);
			},
		});
	},
	get_doc: function (doctype, name, filters) {
		return new Promise((resolve, reject) => {
			vhtfm
				.call({
					method: "vhtfm.client.get",
					type: "GET",
					args: { doctype, name, filters },
					callback: (r) => {
						vhtfm.model.sync(r.message);
						resolve(r.message);
					},
				})
				.fail(reject);
		});
	},
	insert: function (doc) {
		return vhtfm.xcall("vhtfm.client.insert", { doc });
	},
	delete_doc: function (doctype, name) {
		return new Promise((resolve) => {
			vhtfm.call("vhtfm.client.delete", { doctype, name }, (r) => resolve(r.message));
		});
	},
	count: function (doctype, args = {}) {
		let filters = args.filters || {};
		let limit = args.limit;

		// has a filter with childtable?
		const distinct =
			Array.isArray(filters) &&
			filters.some((filter) => {
				return filter[0] !== doctype;
			});

		const fields = [];

		return vhtfm.xcall("vhtfm.desk.reportview.get_count", {
			doctype,
			filters,
			fields,
			distinct,
			limit,
		});
	},
	get_link_options(doctype, txt = "", filters = {}) {
		return new Promise((resolve) => {
			vhtfm.call({
				type: "GET",
				method: "vhtfm.desk.search.search_link",
				args: {
					doctype,
					txt,
					filters,
				},
				callback(r) {
					resolve(r.message);
				},
			});
		});
	},
};
