// Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

vhtfm.provide("vhtfm.ui.toolbar");
vhtfm.provide("vhtfm.search");

vhtfm.ui.toolbar.Toolbar = class {
	constructor() {
		$("header").replaceWith(
			vhtfm.render_template("navbar", {
				avatar: vhtfm.avatar(vhtfm.session.user, "avatar-medium"),
				navbar_settings: vhtfm.boot.navbar_settings,
			})
		);
		$(".dropdown-toggle").dropdown();
		$("#toolbar-user a[href]").click(function () {
			$(this).closest(".dropdown-menu").prev().dropdown("toggle");
		});

		this.setup_awesomebar();
		this.setup_notifications();
		this.setup_help();
		this.setup_read_only_mode();
		this.setup_announcement_widget();
		this.make();
	}

	make() {
		this.bind_events();
		$(document).trigger("toolbar_setup");
		$(".navbar-brand .app-logo").on("click", () => {
			$(".body-sidebar-container")
				.toggleClass("expanded")
				.find(".edit-sidebar-link")
				.addClass("hidden");

			// show close link
			$(".body-sidebar-container")
				.find(".close-sidebar-link")
				.removeClass("hidden")
				.on("click", () => {
					$(".body-sidebar-container").removeClass("expanded");
				});
		});
	}

	bind_events() {
		// clear all custom menus on page change
		$(document).on("page-change", function () {
			$("header .navbar .custom-menu").remove();
		});

		//focus search-modal on show in mobile view
		$("#search-modal").on("shown.bs.modal", function () {
			var search_modal = $(this);
			setTimeout(function () {
				search_modal.find("#modal-search").focus();
			}, 300);
		});
	}

	setup_read_only_mode() {
		if (!vhtfm.boot.read_only) return;

		$("header .read-only-banner").tooltip({
			delay: { show: 600, hide: 100 },
			trigger: "hover",
		});
	}

	setup_announcement_widget() {
		let current_announcement = vhtfm.boot.navbar_settings.announcement_widget;

		if (!current_announcement) return;

		// If an unseen announcement is added, overlook dismiss flag
		if (current_announcement != localStorage.getItem("announcement_widget")) {
			localStorage.removeItem("dismissed_announcement_widget");
			localStorage.setItem("announcement_widget", current_announcement);
		}

		// When an announcement is closed, add dismiss flag
		if (!localStorage.getItem("dismissed_announcement_widget")) {
			let announcement_widget = $(".announcement-widget");
			let close_message = announcement_widget.find(".close-message");
			close_message.on(
				"click",
				() =>
					localStorage.setItem("dismissed_announcement_widget", true) ||
					announcement_widget.addClass("hidden")
			);
		}
	}

	setup_help() {
		if (!vhtfm.boot.desk_settings.notifications) {
			// hide the help section
			$(".navbar .vertical-bar").removeClass("d-sm-block");
			$(".dropdown-help").removeClass("d-lg-block");
			return;
		}
		vhtfm.provide("vhtfm.help");
		vhtfm.help.show_results = show_results;

		this.search = new vhtfm.search.SearchDialog();
		vhtfm.provide("vhtfm.searchdialog");
		vhtfm.searchdialog.search = this.search;

		$(".dropdown-help .dropdown-toggle").on("click", function () {
			$(".dropdown-help input").focus();
		});

		$(".dropdown-help .dropdown-menu").on("click", "input, button", function (e) {
			e.stopPropagation();
		});

		$("#input-help").on("keydown", function (e) {
			if (e.which == 13) {
				$(this).val("");
			}
		});

		$(document).on("page-change", function () {
			var $help_links = $(".dropdown-help #help-links");
			$help_links.html("");

			var route = vhtfm.get_route_str();
			var breadcrumbs = route.split("/");

			var links = [];
			for (let i = 0; i < breadcrumbs.length; i++) {
				var r = route.split("/", i + 1);
				var key = r.join("/");
				var help_links = vhtfm.help.help_links[key] || [];
				links = $.merge(links, help_links);
			}

			if (links.length === 0) {
				$help_links.next().hide();
			} else {
				$help_links.next().show();
			}

			for (let i = 0; i < links.length; i++) {
				var link = links[i];
				var url = link.url;
				$("<a>", {
					href: url,
					class: "dropdown-item",
					text: __(link.label),
					target: "_blank",
				}).appendTo($help_links);
			}

			$(".dropdown-help .dropdown-menu").on("click", "a", show_results);
		});

		var $result_modal = vhtfm.get_modal("", "");
		$result_modal.addClass("help-modal");

		$(document).on("click", ".help-modal a", show_results);

		function show_results(e) {
			//edit links
			var href = e.target.href;
			if (href.indexOf("blob") > 0) {
				window.open(href, "_blank");
			}
			var path = $(e.target).attr("data-path");
			if (path) {
				e.preventDefault();
			}
		}
	}

	setup_awesomebar() {
		if (vhtfm.boot.desk_settings.search_bar) {
			let awesome_bar = new vhtfm.search.AwesomeBar();
			awesome_bar.setup("#navbar-search");

			vhtfm.search.utils.make_function_searchable(
				vhtfm.utils.generate_tracking_url,
				__("Generate Tracking URL")
			);

			if (vhtfm.model.can_read("RQ Job")) {
				vhtfm.search.utils.make_function_searchable(function () {
					vhtfm.set_route("List", "RQ Job");
				}, __("Background Jobs"));
			}
		}
	}

	setup_notifications() {
		if (vhtfm.boot.desk_settings.notifications && vhtfm.session.user !== "Guest") {
			this.notifications = new vhtfm.ui.Notifications();
		}
	}
};

$.extend(vhtfm.ui.toolbar, {
	add_dropdown_button: function (parent, label, click, icon) {
		var menu = vhtfm.ui.toolbar.get_menu(parent);
		if (menu.find("li:not(.custom-menu)").length && !menu.find(".divider").length) {
			vhtfm.ui.toolbar.add_menu_divider(menu);
		}

		return $(
			'<li class="custom-menu"><a><i class="fa-fw ' + icon + '"></i> ' + label + "</a></li>"
		)
			.insertBefore(menu.find(".divider"))
			.find("a")
			.click(function () {
				click.apply(this);
			});
	},
	get_menu: function (label) {
		return $("#navbar-" + label.toLowerCase());
	},
	add_menu_divider: function (menu) {
		menu = typeof menu == "string" ? vhtfm.ui.toolbar.get_menu(menu) : menu;

		$('<li class="divider custom-menu"></li>').prependTo(menu);
	},
	add_icon_link(route, icon, index, class_name) {
		let parent_element = $(".navbar-right").get(0);
		let new_element = $(`<li class="${class_name}">
			<a class="btn" href="${route}" title="${vhtfm.utils.to_title_case(
			class_name,
			true
		)}" aria-haspopup="true" aria-expanded="true">
				<div>
					<i class="octicon ${icon}"></i>
				</div>
			</a>
		</li>`).get(0);

		parent_element.insertBefore(new_element, parent_element.children[index]);
	},
	toggle_full_width() {
		let fullwidth = JSON.parse(localStorage.container_fullwidth || "false");
		fullwidth = !fullwidth;
		localStorage.container_fullwidth = fullwidth;
		vhtfm.ui.toolbar.set_fullwidth_if_enabled();
		$(document.body).trigger("toggleFullWidth");
	},
	set_fullwidth_if_enabled() {
		let fullwidth = JSON.parse(localStorage.container_fullwidth || "false");
		$(document.body).toggleClass("full-width", fullwidth);
	},
	show_shortcuts(e) {
		e.preventDefault();
		vhtfm.ui.keys.show_keyboard_shortcut_dialog();
		return false;
	},
});

vhtfm.ui.toolbar.clear_cache = vhtfm.utils.throttle(function () {
	vhtfm.assets.clear_local_storage();
	vhtfm.xcall("vhtfm.sessions.clear").then((message) => {
		vhtfm.show_alert({
			message: message,
			indicator: "info",
		});
		location.reload(true);
	});
}, 10000);

vhtfm.ui.toolbar.show_about = function () {
	try {
		vhtfm.ui.misc.about();
	} catch (e) {
		console.log(e);
	}
	return false;
};

vhtfm.ui.toolbar.route_to_user = function () {
	vhtfm.set_route("Form", "User", vhtfm.session.user);
};

vhtfm.ui.toolbar.view_website = function () {
	let website_tab = window.open();
	website_tab.opener = null;
	website_tab.location = "/index";
};

vhtfm.ui.toolbar.setup_session_defaults = function () {
	let fields = [];
	vhtfm.call({
		method: "vhtfm.core.doctype.session_default_settings.session_default_settings.get_session_default_values",
		callback: function (data) {
			fields = JSON.parse(data.message);
			let perms = vhtfm.perm.get_perm("Session Default Settings");
			//add settings button only if user is a System Manager or has permission on 'Session Default Settings'
			if (vhtfm.user_roles.includes("System Manager") || perms[0].read == 1) {
				fields[fields.length] = {
					fieldname: "settings",
					fieldtype: "Button",
					label: __("Settings"),
					click: () => {
						vhtfm.set_route(
							"Form",
							"Session Default Settings",
							"Session Default Settings"
						);
					},
				};
			}
			vhtfm.prompt(
				fields,
				function (values) {
					//if default is not set for a particular field in prompt
					fields.forEach(function (d) {
						if (!values[d.fieldname]) {
							values[d.fieldname] = "";
						}
					});
					vhtfm.call({
						method: "vhtfm.core.doctype.session_default_settings.session_default_settings.set_session_default_values",
						args: {
							default_values: values,
						},
						callback: function (data) {
							if (data.message == "success") {
								vhtfm.show_alert({
									message: __("Session Defaults Saved"),
									indicator: "green",
								});
								vhtfm.ui.toolbar.clear_cache();
							} else {
								vhtfm.show_alert({
									message: __(
										"An error occurred while setting Session Defaults"
									),
									indicator: "red",
								});
							}
						},
					});
				},
				__("Session Defaults"),
				__("Save")
			);
		},
	});
};
