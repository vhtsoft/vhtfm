import "./alt_keyboard_shortcuts";

vhtfm.provide("vhtfm.ui.keys.handlers");

vhtfm.ui.keys.setup = function () {
	$(window).on("keydown", function (e) {
		var key = vhtfm.ui.keys.get_key(e);
		if (vhtfm.ui.keys.handlers[key]) {
			var out = null;
			for (var i = 0, l = vhtfm.ui.keys.handlers[key].length; i < l; i++) {
				var handler = vhtfm.ui.keys.handlers[key][i];
				var _out = handler.apply(this, [e]);
				if (_out === false) {
					out = _out;
				}
			}
			return out;
		}
	});
};

let standard_shortcuts = [];
vhtfm.ui.keys.standard_shortcuts = standard_shortcuts;
vhtfm.ui.keys.add_shortcut = ({
	shortcut,
	action,
	description,
	page,
	target,
	condition,
	ignore_inputs = false,
} = {}) => {
	if (target instanceof jQuery) {
		let $target = target;
		action = () => {
			$target[0].click();
		};
	}
	if (!condition) {
		condition = () => true;
	}
	let handler = (e) => {
		let $focused_element = $(document.activeElement);
		let is_input_focused = $focused_element.is(
			"input, select, textarea, [contenteditable=true]"
		);
		if (is_input_focused && !ignore_inputs) return;
		if (!condition()) return;

		if (action && (!page || page.wrapper.is(":visible"))) {
			let prevent_default = action(e);
			// prevent default if true is explicitly returned
			// or nothing returned (undefined)
			if (prevent_default || prevent_default === undefined) {
				e.preventDefault();
			}
		}
	};
	// monkey patch page to handler
	handler.page = page;
	// remove handler with the same page attached to it
	vhtfm.ui.keys.off(shortcut, page);
	// attach new handler
	vhtfm.ui.keys.on(shortcut, handler);

	// update standard shortcut list
	let existing_shortcut_index = standard_shortcuts.findIndex((s) => s.shortcut === shortcut);
	let new_shortcut = { shortcut, action, description, page, condition };
	if (existing_shortcut_index === -1) {
		standard_shortcuts.push(new_shortcut);
	} else {
		standard_shortcuts[existing_shortcut_index] = new_shortcut;
	}
};

vhtfm.ui.keys.show_keyboard_shortcut_dialog = () => {
	if (vhtfm.ui.keys.is_dialog_shown) return;

	let global_shortcuts = standard_shortcuts.filter((shortcut) => !shortcut.page);
	let current_page_shortcuts = standard_shortcuts.filter(
		(shortcut) => shortcut.page && shortcut.page === window.cur_page.page.page
	);

	let grid_shortcuts = standard_shortcuts.filter(
		(shortcut) => shortcut.page && shortcut.page === window.cur_page.page.frm
	);

	function generate_shortcuts_html(shortcuts, heading) {
		if (!shortcuts.length) {
			return "";
		}
		let html = shortcuts
			.filter((s) => (s.condition ? s.condition() : true))
			.filter((s) => !!s.description)
			.map((shortcut) => {
				let shortcut_label = shortcut.shortcut
					.split("+")
					.map(vhtfm.utils.to_title_case)
					.join("+");
				if (vhtfm.utils.is_mac()) {
					shortcut_label = shortcut_label.replace("Ctrl", "⌘").replace("Alt", "⌥");
				}

				shortcut_label = shortcut_label.replace("Shift", "⇧");

				return `<tr>
					<td width="40%"><kbd>${shortcut_label}</kbd></td>
					<td width="60%">${shortcut.description || ""}</td>
				</tr>`;
			})
			.join("");
		if (!html) return "";

		html = `<h5 style="margin: 0;">${heading}</h5>
			<table style="margin-top: 10px;" class="table table-bordered">
				${html}
			</table>`;
		return html;
	}

	let global_shortcuts_html = generate_shortcuts_html(global_shortcuts, __("Global Shortcuts"));
	let current_page_shortcuts_html = generate_shortcuts_html(
		current_page_shortcuts,
		__("Page Shortcuts")
	);
	let grid_shortcuts_html = generate_shortcuts_html(grid_shortcuts, __("Grid Shortcuts"));

	let dialog = new vhtfm.ui.Dialog({
		title: __("Keyboard Shortcuts"),
		on_hide() {
			vhtfm.ui.keys.is_dialog_shown = false;
		},
	});

	dialog.$body.append(global_shortcuts_html);
	dialog.$body.append(current_page_shortcuts_html);
	dialog.$body.append(grid_shortcuts_html);
	dialog.$body.append(`
		<div class="text-muted">
			${__("Press Alt Key to trigger additional shortcuts in Menu and Sidebar")}
		</div>
	`);

	dialog.show();
	vhtfm.ui.keys.is_dialog_shown = true;
};

vhtfm.ui.keys.get_key = function (e) {
	var keycode = e.keyCode || e.which;
	var key = vhtfm.ui.keys.key_map[keycode] || String.fromCharCode(keycode);

	if (e.ctrlKey || e.metaKey) {
		// add ctrl+ the key
		key = "ctrl+" + key;
	}
	if (e.shiftKey) {
		// add shift+ the key
		key = "shift+" + key;
	}
	if (e.altKey) {
		// add alt+ the key
		key = "alt+" + key;
	}
	if (e.altKey && e.ctrlKey) {
		// add alt+ctrl+ the key or single key e.g f1,f2,etc..
		return key.toLowerCase();
	}
	return key.toLowerCase();
};

vhtfm.ui.keys.on = function (key, handler) {
	if (!vhtfm.ui.keys.handlers[key]) {
		vhtfm.ui.keys.handlers[key] = [];
	}
	vhtfm.ui.keys.handlers[key].push(handler);
};

vhtfm.ui.keys.off = function (key, page) {
	let handlers = vhtfm.ui.keys.handlers[key];
	if (!handlers || handlers.length === 0) return;
	vhtfm.ui.keys.handlers[key] = handlers.filter((h) => {
		if (!page) return false;
		return h.page !== page;
	});
};

vhtfm.ui.keys.add_shortcut({
	shortcut: "ctrl+s",
	action: function (e) {
		document.activeElement?.blur();
		vhtfm.app.trigger_primary_action();
		e.preventDefault();
		return false;
	},
	description: __("Trigger Primary Action"),
	ignore_inputs: true,
});

vhtfm.ui.keys.add_shortcut({
	shortcut: "ctrl+g",
	action: function (e) {
		$("#navbar-search").focus();
		e.preventDefault();
		return false;
	},
	description: __("Open Awesomebar"),
});

vhtfm.ui.keys.add_shortcut({
	shortcut: "ctrl+k",
	action: function (e) {
		$("#navbar-search").focus();
		e.preventDefault();
		return false;
	},
	description: __("Open Awesomebar"),
});

vhtfm.ui.keys.add_shortcut({
	shortcut: "ctrl+h",
	action: function (e) {
		e.preventDefault();
		$(".navbar-home img").click();
	},
	description: __("Navigate Home"),
});

vhtfm.ui.keys.add_shortcut({
	shortcut: "alt+s",
	action: function (e) {
		e.preventDefault();
		$(".dropdown-navbar-user button").eq(0).click();
	},
	description: __("Open Settings"),
});

vhtfm.ui.keys.add_shortcut({
	shortcut: "shift+/",
	action: function () {
		vhtfm.ui.keys.show_keyboard_shortcut_dialog();
	},
	description: __("Show Keyboard Shortcuts"),
});

vhtfm.ui.keys.add_shortcut({
	shortcut: "alt+h",
	action: function (e) {
		e.preventDefault();
		$(".dropdown-help button").eq(0).click();
	},
	description: __("Open Help"),
});

vhtfm.ui.keys.on("escape", function (e) {
	handle_escape_key();
});

vhtfm.ui.keys.on("esc", function (e) {
	handle_escape_key();
});

vhtfm.ui.keys.on("enter", function (e) {
	if (window.cur_dialog && cur_dialog.confirm_dialog) {
		cur_dialog.get_primary_btn().trigger("click");
	}
});

vhtfm.ui.keys.on("ctrl+down", function (e) {
	const grid_row = vhtfm.ui.form.get_open_grid_form();
	if (grid_row?.has_next()) {
		grid_row.toggle_view(false, function () {
			grid_row.open_next();
		});
	} else {
		e.preventDefault();
	}
});

vhtfm.ui.keys.on("ctrl+up", function (e) {
	const grid_row = vhtfm.ui.form.get_open_grid_form();
	if (grid_row?.has_prev()) {
		grid_row.toggle_view(false, function () {
			grid_row.open_prev();
		});
	} else {
		e.preventDefault();
	}
});

vhtfm.ui.keys.add_shortcut({
	shortcut: "shift+ctrl+r",
	action: function () {
		vhtfm.ui.toolbar.clear_cache();
	},
	description: __("Clear Cache and Reload"),
});

vhtfm.ui.keys.key_map = {
	8: "backspace",
	9: "tab",
	13: "enter",
	16: "shift",
	17: "ctrl",
	91: "meta",
	18: "alt",
	27: "escape",
	37: "left",
	39: "right",
	38: "up",
	40: "down",
	32: "space",
	112: "f1",
	113: "f2",
	114: "f3",
	115: "f4",
	116: "f5",
	191: "/",
	188: "<",
	190: ">",
};

"abcdefghijklmnopqrstuvwxyz".split("").forEach((letter, i) => {
	vhtfm.ui.keys.key_map[65 + i] = letter;
});

// keyCode map
vhtfm.ui.keyCode = {
	ESCAPE: 27,
	LEFT: 37,
	RIGHT: 39,
	UP: 38,
	DOWN: 40,
	ENTER: 13,
	TAB: 9,
	SPACE: 32,
	BACKSPACE: 8,
};

function handle_escape_key() {
	close_grid_and_dialog();
	document.activeElement?.blur();
}

function close_grid_and_dialog() {
	// close open grid row
	var open_row = $(".grid-row-open");
	if (open_row.length) {
		var grid_row = open_row.data("grid_row");
		grid_row.toggle_view(false);
		return false;
	}

	// close open dialog
	if (cur_dialog && !cur_dialog.no_cancel_flag && !cur_dialog.static) {
		cur_dialog.cancel();
		return false;
	}
}
