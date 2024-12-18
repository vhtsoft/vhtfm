// Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

// provide a namespace
if (!window.vhtfm) window.vhtfm = {};

vhtfm.provide = function (namespace) {
	// docs: create a namespace //
	var nsl = namespace.split(".");
	var parent = window;
	for (var i = 0; i < nsl.length; i++) {
		var n = nsl[i];
		if (!parent[n]) {
			parent[n] = {};
		}
		parent = parent[n];
	}
	return parent;
};

vhtfm.provide("locals");
vhtfm.provide("vhtfm.flags");
vhtfm.provide("vhtfm.settings");
vhtfm.provide("vhtfm.utils");
vhtfm.provide("vhtfm.ui.form");
vhtfm.provide("vhtfm.modules");
vhtfm.provide("vhtfm.templates");
vhtfm.provide("vhtfm.test_data");
vhtfm.provide("vhtfm.utils");
vhtfm.provide("vhtfm.model");
vhtfm.provide("vhtfm.user");
vhtfm.provide("vhtfm.session");
vhtfm.provide("vhtfm._messages");
vhtfm.provide("locals.DocType");

// for listviews
vhtfm.provide("vhtfm.listview_settings");
vhtfm.provide("vhtfm.tour");
vhtfm.provide("vhtfm.listview_parent_route");

// constants
window.NEWLINE = "\n";
window.TAB = 9;
window.UP_ARROW = 38;
window.DOWN_ARROW = 40;

// proxy for user globals defined in desk.js

// API globals
window.cur_frm = null;
