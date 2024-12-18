// Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt
/* eslint-disable no-console */

// __('Modules') __('Domains') __('Places') __('Administration') # for translation, don't remove

vhtfm.start_app = function () {
	if (!vhtfm.Application) return;
	vhtfm.assets.check();
	vhtfm.provide("vhtfm.app");
	vhtfm.provide("vhtfm.desk");
	vhtfm.app = new vhtfm.Application();
};

$(document).ready(function () {
	if (!vhtfm.utils.supportsES6) {
		vhtfm.msgprint({
			indicator: "red",
			title: __("Browser not supported"),
			message: __(
				"Some of the features might not work in your browser. Please update your browser to the latest version."
			),
		});
	}
	vhtfm.start_app();
});

vhtfm.Application = class Application {
	constructor() {
		this.startup();
	}

	startup() {
		vhtfm.realtime.init();
		vhtfm.model.init();

		this.load_bootinfo();
		this.load_user_permissions();
		this.make_nav_bar();
		this.make_sidebar();
		this.set_favicon();
		this.set_fullwidth_if_enabled();
		this.add_browser_class();
		this.setup_energy_point_listeners();
		this.setup_copy_doc_listener();
		this.setup_broadcast_listeners();

		vhtfm.ui.keys.setup();

		this.setup_theme();

		// page container
		this.make_page_container();
		this.setup_tours();
		this.set_route();

		// trigger app startup
		$(document).trigger("startup");
		$(document).trigger("app_ready");

		this.show_notices();
		this.show_notes();

		if (vhtfm.ui.startup_setup_dialog && !vhtfm.boot.setup_complete) {
			vhtfm.ui.startup_setup_dialog.pre_show();
			vhtfm.ui.startup_setup_dialog.show();
		}

		// listen to build errors
		this.setup_build_events();

		if (vhtfm.sys_defaults.email_user_password) {
			var email_list = vhtfm.sys_defaults.email_user_password.split(",");
			for (var u in email_list) {
				if (email_list[u] === vhtfm.user.name) {
					this.set_password(email_list[u]);
				}
			}
		}

		// REDESIGN-TODO: Fix preview popovers
		this.link_preview = new vhtfm.ui.LinkPreview();

		vhtfm.broadcast.emit("boot", {
			csrf_token: vhtfm.csrf_token,
			user: vhtfm.session.user,
		});
	}

	make_sidebar() {
		this.sidebar = new vhtfm.ui.Sidebar({});
	}

	setup_theme() {
		vhtfm.ui.keys.add_shortcut({
			shortcut: "shift+ctrl+g",
			description: __("Switch Theme"),
			action: () => {
				if (vhtfm.theme_switcher && vhtfm.theme_switcher.dialog.is_visible) {
					vhtfm.theme_switcher.hide();
				} else {
					vhtfm.theme_switcher = new vhtfm.ui.ThemeSwitcher();
					vhtfm.theme_switcher.show();
				}
			},
		});

		vhtfm.ui.add_system_theme_switch_listener();
		const root = document.documentElement;

		const observer = new MutationObserver(() => {
			vhtfm.ui.set_theme();
		});
		observer.observe(root, {
			attributes: true,
			attributeFilter: ["data-theme-mode"],
		});

		vhtfm.ui.set_theme();
	}

	setup_tours() {
		if (
			!window.Cypress &&
			vhtfm.boot.onboarding_tours &&
			vhtfm.boot.user.onboarding_status != null
		) {
			let pending_tours = !vhtfm.boot.onboarding_tours.every(
				(tour) => vhtfm.boot.user.onboarding_status[tour[0]]?.is_complete
			);
			if (pending_tours && vhtfm.boot.onboarding_tours.length > 0) {
				vhtfm.require("onboarding_tours.bundle.js", () => {
					vhtfm.utils.sleep(1000).then(() => {
						vhtfm.ui.init_onboarding_tour();
					});
				});
			}
		}
	}

	show_notices() {
		if (vhtfm.boot.messages) {
			vhtfm.msgprint(vhtfm.boot.messages);
		}

		if (vhtfm.user_roles.includes("System Manager")) {
			// delayed following requests to make boot faster
			setTimeout(() => {
				this.show_change_log();
				this.show_update_available();
			}, 1000);
		}

		if (!vhtfm.boot.developer_mode) {
			let console_security_message = __(
				"Using this console may allow attackers to impersonate you and steal your information. Do not enter or paste code that you do not understand."
			);
			console.log(`%c${console_security_message}`, "font-size: large");
		}

		vhtfm.realtime.on("version-update", function () {
			var dialog = vhtfm.msgprint({
				message: __(
					"The application has been updated to a new version, please refresh this page"
				),
				indicator: "green",
				title: __("Version Updated"),
			});
			dialog.set_primary_action(__("Refresh"), function () {
				location.reload(true);
			});
			dialog.get_close_btn().toggle(false);
		});
	}

	set_route() {
		if (vhtfm.boot && localStorage.getItem("session_last_route")) {
			vhtfm.set_route(localStorage.getItem("session_last_route"));
			localStorage.removeItem("session_last_route");
		} else {
			// route to home page
			vhtfm.router.route();
		}
		vhtfm.router.on("change", () => {
			$(".tooltip").hide();
		});
	}

	set_password(user) {
		var me = this;
		vhtfm.call({
			method: "vhtfm.core.doctype.user.user.get_email_awaiting",
			args: {
				user: user,
			},
			callback: function (email_account) {
				email_account = email_account["message"];
				if (email_account) {
					var i = 0;
					if (i < email_account.length) {
						me.email_password_prompt(email_account, user, i);
					}
				}
			},
		});
	}

	email_password_prompt(email_account, user, i) {
		var me = this;
		const email_id = email_account[i]["email_id"];
		let d = new vhtfm.ui.Dialog({
			title: __("Password missing in Email Account"),
			fields: [
				{
					fieldname: "password",
					fieldtype: "Password",
					label: __(
						"Please enter the password for: <b>{0}</b>",
						[email_id],
						"Email Account"
					),
					reqd: 1,
				},
				{
					fieldname: "submit",
					fieldtype: "Button",
					label: __("Submit", null, "Submit password for Email Account"),
				},
			],
		});
		d.get_input("submit").on("click", function () {
			//setup spinner
			d.hide();
			var s = new vhtfm.ui.Dialog({
				title: __("Checking one moment"),
				fields: [
					{
						fieldtype: "HTML",
						fieldname: "checking",
					},
				],
			});
			s.fields_dict.checking.$wrapper.html('<i class="fa fa-spinner fa-spin fa-4x"></i>');
			s.show();
			vhtfm.call({
				method: "vhtfm.email.doctype.email_account.email_account.set_email_password",
				args: {
					email_account: email_account[i]["email_account"],
					password: d.get_value("password"),
				},
				callback: function (passed) {
					s.hide();
					d.hide(); //hide waiting indication
					if (!passed["message"]) {
						vhtfm.show_alert(
							{ message: __("Login Failed please try again"), indicator: "error" },
							5
						);
						me.email_password_prompt(email_account, user, i);
					} else {
						if (i + 1 < email_account.length) {
							i = i + 1;
							me.email_password_prompt(email_account, user, i);
						}
					}
				},
			});
		});
		d.show();
	}
	load_bootinfo() {
		if (vhtfm.boot) {
			this.setup_workspaces();
			vhtfm.model.sync(vhtfm.boot.docs);
			this.check_metadata_cache_status();
			this.set_globals();
			this.sync_pages();
			vhtfm.router.setup();
			this.setup_moment();
			if (vhtfm.boot.print_css) {
				vhtfm.dom.set_style(vhtfm.boot.print_css, "print-style");
			}
			vhtfm.user.name = vhtfm.boot.user.name;
			vhtfm.router.setup();
		} else {
			this.set_as_guest();
		}
	}

	setup_workspaces() {
		vhtfm.modules = {};
		vhtfm.workspaces = {};
		vhtfm.boot.allowed_workspaces = vhtfm.boot.sidebar_pages.pages;

		for (let page of vhtfm.boot.allowed_workspaces || []) {
			vhtfm.modules[page.module] = page;
			vhtfm.workspaces[vhtfm.router.slug(page.name)] = page;
		}
	}

	load_user_permissions() {
		vhtfm.defaults.load_user_permission_from_boot();

		vhtfm.realtime.on(
			"update_user_permissions",
			vhtfm.utils.debounce(() => {
				vhtfm.defaults.update_user_permissions();
			}, 500)
		);
	}

	check_metadata_cache_status() {
		if (vhtfm.boot.metadata_version != localStorage.metadata_version) {
			vhtfm.assets.clear_local_storage();
			vhtfm.assets.init_local_storage();
		}
	}

	set_globals() {
		vhtfm.session.user = vhtfm.boot.user.name;
		vhtfm.session.logged_in_user = vhtfm.boot.user.name;
		vhtfm.session.user_email = vhtfm.boot.user.email;
		vhtfm.session.user_fullname = vhtfm.user_info().fullname;

		vhtfm.user_defaults = vhtfm.boot.user.defaults;
		vhtfm.user_roles = vhtfm.boot.user.roles;
		vhtfm.sys_defaults = vhtfm.boot.sysdefaults;

		vhtfm.ui.py_date_format = vhtfm.boot.sysdefaults.date_format
			.replace("dd", "%d")
			.replace("mm", "%m")
			.replace("yyyy", "%Y");
		vhtfm.boot.user.last_selected_values = {};
	}
	sync_pages() {
		// clear cached pages if timestamp is not found
		if (localStorage["page_info"]) {
			vhtfm.boot.allowed_pages = [];
			var page_info = JSON.parse(localStorage["page_info"]);
			$.each(vhtfm.boot.page_info, function (name, p) {
				if (!page_info[name] || page_info[name].modified != p.modified) {
					delete localStorage["_page:" + name];
				}
				vhtfm.boot.allowed_pages.push(name);
			});
		} else {
			vhtfm.boot.allowed_pages = Object.keys(vhtfm.boot.page_info);
		}
		localStorage["page_info"] = JSON.stringify(vhtfm.boot.page_info);
	}
	set_as_guest() {
		vhtfm.session.user = "Guest";
		vhtfm.session.user_email = "";
		vhtfm.session.user_fullname = "Guest";

		vhtfm.user_defaults = {};
		vhtfm.user_roles = ["Guest"];
		vhtfm.sys_defaults = {};
	}
	make_page_container() {
		if ($("#body").length) {
			$(".splash").remove();
			vhtfm.temp_container = $("<div id='temp-container' style='display: none;'>").appendTo(
				"body"
			);
			vhtfm.container = new vhtfm.views.Container();
		}
	}
	make_nav_bar() {
		// toolbar
		if (vhtfm.boot && vhtfm.boot.home_page !== "setup-wizard") {
			vhtfm.vhtfm_toolbar = new vhtfm.ui.toolbar.Toolbar();
		}
	}
	logout() {
		var me = this;
		me.logged_out = true;
		return vhtfm.call({
			method: "logout",
			callback: function (r) {
				if (r.exc) {
					return;
				}
				me.redirect_to_login();
			},
		});
	}
	handle_session_expired() {
		vhtfm.app.redirect_to_login();
	}
	redirect_to_login() {
		window.location.href = `/login?redirect-to=${encodeURIComponent(
			window.location.pathname + window.location.search
		)}`;
	}
	set_favicon() {
		var link = $('link[type="image/x-icon"]').remove().attr("href");
		$('<link rel="shortcut icon" href="' + link + '" type="image/x-icon">').appendTo("head");
		$('<link rel="icon" href="' + link + '" type="image/x-icon">').appendTo("head");
	}
	trigger_primary_action() {
		// to trigger change event on active input before triggering primary action
		$(document.activeElement).blur();
		// wait for possible JS validations triggered after blur (it might change primary button)
		setTimeout(() => {
			if (window.cur_dialog && cur_dialog.display && !cur_dialog.is_minimized) {
				// trigger primary
				cur_dialog.get_primary_btn().trigger("click");
			} else if (cur_frm && cur_frm.page.btn_primary.is(":visible")) {
				cur_frm.page.btn_primary.trigger("click");
			} else if (vhtfm.container.page.save_action) {
				vhtfm.container.page.save_action();
			}
		}, 100);
	}

	show_change_log() {
		var me = this;
		let change_log = vhtfm.boot.change_log;

		// vhtfm.boot.change_log = [{
		// 	"change_log": [
		// 		[<version>, <change_log in markdown>],
		// 		[<version>, <change_log in markdown>],
		// 	],
		// 	"description": "ERP made simple",
		// 	"title": "ERPNext",
		// 	"version": "12.2.0"
		// }];

		if (
			!Array.isArray(change_log) ||
			!change_log.length ||
			window.Cypress ||
			cint(vhtfm.boot.sysdefaults.disable_change_log_notification)
		) {
			return;
		}

		// Iterate over changelog
		var change_log_dialog = vhtfm.msgprint({
			message: vhtfm.render_template("change_log", { change_log: change_log }),
			title: __("Updated To A New Version 🎉"),
			wide: true,
		});
		change_log_dialog.keep_open = true;
		change_log_dialog.custom_onhide = function () {
			vhtfm.call({
				method: "vhtfm.utils.change_log.update_last_known_versions",
			});
			me.show_notes();
		};
	}

	show_update_available() {
		if (!vhtfm.boot.has_app_updates) return;
		vhtfm.xcall("vhtfm.utils.change_log.show_update_popup");
	}

	add_browser_class() {
		$("html").addClass(vhtfm.utils.get_browser().name.toLowerCase());
	}

	set_fullwidth_if_enabled() {
		vhtfm.ui.toolbar.set_fullwidth_if_enabled();
	}

	show_notes() {
		var me = this;
		if (vhtfm.boot.notes.length) {
			vhtfm.boot.notes.forEach(function (note) {
				if (!note.seen || note.notify_on_every_login) {
					var d = vhtfm.msgprint({ message: note.content, title: note.title });
					d.keep_open = true;
					d.custom_onhide = function () {
						note.seen = true;

						// Mark note as read if the Notify On Every Login flag is not set
						if (!note.notify_on_every_login) {
							vhtfm.call({
								method: "vhtfm.desk.doctype.note.note.mark_as_seen",
								args: {
									note: note.name,
								},
							});
						}

						// next note
						me.show_notes();
					};
				}
			});
		}
	}

	setup_build_events() {
		if (vhtfm.boot.developer_mode) {
			vhtfm.require("build_events.bundle.js");
		}
	}

	setup_energy_point_listeners() {
		vhtfm.realtime.on("energy_point_alert", (message) => {
			vhtfm.show_alert(message);
		});
	}

	setup_copy_doc_listener() {
		$("body").on("paste", (e) => {
			try {
				let pasted_data = vhtfm.utils.get_clipboard_data(e);
				let doc = JSON.parse(pasted_data);
				if (doc.doctype) {
					e.preventDefault();
					const sleep = vhtfm.utils.sleep;

					vhtfm.dom.freeze(__("Creating {0}", [doc.doctype]) + "...");
					// to avoid abrupt UX
					// wait for activity feedback
					sleep(500).then(() => {
						let res = vhtfm.model.with_doctype(doc.doctype, () => {
							let newdoc = vhtfm.model.copy_doc(doc);
							newdoc.__newname = doc.name;
							delete doc.name;
							newdoc.idx = null;
							newdoc.__run_link_triggers = false;
							vhtfm.set_route("Form", newdoc.doctype, newdoc.name);
							vhtfm.dom.unfreeze();
						});
						res && res.fail?.(vhtfm.dom.unfreeze);
					});
				}
			} catch (e) {
				//
			}
		});
	}

	/// Setup event listeners for events across browser tabs / web workers.
	setup_broadcast_listeners() {
		// booted in another tab -> refresh csrf to avoid invalid requests.
		vhtfm.broadcast.on("boot", ({ csrf_token, user }) => {
			if (user && user != vhtfm.session.user) {
				vhtfm.msgprint({
					message: __(
						"You've logged in as another user from another tab. Refresh this page to continue using system."
					),
					title: __("User Changed"),
					primary_action: {
						label: __("Refresh"),
						action: () => {
							window.location.reload();
						},
					},
				});
				return;
			}

			if (csrf_token) {
				// If user re-logged in then their other tabs won't be usable without this update.
				vhtfm.csrf_token = csrf_token;
			}
		});
	}

	setup_moment() {
		moment.updateLocale("en", {
			week: {
				dow: vhtfm.datetime.get_first_day_of_the_week_index(),
			},
		});
		moment.locale("en");
		moment.user_utc_offset = moment().utcOffset();
		if (vhtfm.boot.timezone_info) {
			moment.tz.add(vhtfm.boot.timezone_info);
		}
	}
};

vhtfm.get_module = function (m, default_module) {
	var module = vhtfm.modules[m] || default_module;
	if (!module) {
		return;
	}

	if (module._setup) {
		return module;
	}

	if (!module.label) {
		module.label = m;
	}

	if (!module._label) {
		module._label = __(module.label);
	}

	module._setup = true;

	return module;
};
