// Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

vhtfm.provide("vhtfm.views.pageview");
vhtfm.provide("vhtfm.standard_pages");

vhtfm.views.pageview = {
	with_page: function (name, callback) {
		if (vhtfm.standard_pages[name]) {
			if (!vhtfm.pages[name]) {
				vhtfm.standard_pages[name]();
			}
			callback();
			return;
		}

		if (
			(locals.Page && locals.Page[name] && locals.Page[name].script) ||
			name == window.page_name
		) {
			// already loaded
			callback();
		} else if (localStorage["_page:" + name] && vhtfm.boot.developer_mode != 1) {
			// cached in local storage
			vhtfm.model.sync(JSON.parse(localStorage["_page:" + name]));
			callback();
		} else if (name) {
			// get fresh
			return vhtfm.call({
				method: "vhtfm.desk.desk_page.getpage",
				args: { name: name },
				callback: function (r) {
					if (!r.docs._dynamic_page) {
						try {
							localStorage["_page:" + name] = JSON.stringify(r.docs);
						} catch (e) {
							console.warn(e);
						}
					}
					callback();
				},
				freeze: true,
			});
		}
	},

	show: function (name) {
		if (!name) {
			name = vhtfm.boot ? vhtfm.boot.home_page : window.page_name;
		}
		vhtfm.model.with_doctype("Page", function () {
			vhtfm.views.pageview.with_page(name, function (r) {
				if (r && r.exc) {
					if (!r["403"]) vhtfm.show_not_found(name);
				} else if (!vhtfm.pages[name]) {
					new vhtfm.views.Page(name);
				}
				vhtfm.container.change_to(name);
			});
		});
	},
};

vhtfm.views.Page = class Page {
	constructor(name) {
		this.name = name;
		var me = this;

		// web home page
		if (name == window.page_name) {
			this.wrapper = document.getElementById("page-" + name);
			this.wrapper.label = document.title || window.page_name;
			this.wrapper.page_name = window.page_name;
			vhtfm.pages[window.page_name] = this.wrapper;
		} else {
			this.pagedoc = locals.Page[this.name];
			if (!this.pagedoc) {
				vhtfm.show_not_found(name);
				return;
			}
			this.wrapper = vhtfm.container.add_page(this.name);
			this.wrapper.page_name = this.pagedoc.name;

			// set content, script and style
			if (this.pagedoc.content) this.wrapper.innerHTML = this.pagedoc.content;
			vhtfm.dom.eval(this.pagedoc.__script || this.pagedoc.script || "");
			vhtfm.dom.set_style(this.pagedoc.style || "");

			// set breadcrumbs
			vhtfm.breadcrumbs.add(this.pagedoc.module || null);
		}

		this.trigger_page_event("on_page_load");

		// set events
		$(this.wrapper).on("show", function () {
			window.cur_frm = null;
			me.trigger_page_event("on_page_show");
			me.trigger_page_event("refresh");
		});
	}

	trigger_page_event(eventname) {
		var me = this;
		if (me.wrapper[eventname]) {
			me.wrapper[eventname](me.wrapper);
		}
	}
};

vhtfm.show_not_found = function (page_name) {
	vhtfm.show_message_page({
		page_name: page_name,
		message: __("Sorry! I could not find what you were looking for."),
		img: "/assets/vhtfm/images/ui/bubble-tea-sorry.svg",
	});
};

vhtfm.show_not_permitted = function (page_name) {
	vhtfm.show_message_page({
		page_name: page_name,
		message: __("Sorry! You are not permitted to view this page."),
		img: "/assets/vhtfm/images/ui/bubble-tea-sorry.svg",
		// icon: "octicon octicon-circle-slash"
	});
};

vhtfm.show_message_page = function (opts) {
	// opts can include `page_name`, `message`, `icon` or `img`
	if (!opts.page_name) {
		opts.page_name = vhtfm.get_route_str();
	}

	if (opts.icon) {
		opts.img = repl('<span class="%(icon)s message-page-icon"></span> ', opts);
	} else if (opts.img) {
		opts.img = repl('<img src="%(img)s" class="message-page-image">', opts);
	}

	var page = vhtfm.pages[opts.page_name] || vhtfm.container.add_page(opts.page_name);
	$(page).html(
		repl(
			'<div class="page message-page">\
			<div class="text-center message-page-content">\
				%(img)s\
				<p class="lead">%(message)s</p>\
				<a class="btn btn-default btn-sm btn-home" href="/app">%(home)s</a>\
			</div>\
		</div>',
			{
				img: opts.img || "",
				message: opts.message || "",
				home: __("Home"),
			}
		)
	);

	vhtfm.container.change_to(opts.page_name);
};
