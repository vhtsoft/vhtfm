vhtfm.user_info = function (uid) {
	if (!uid) uid = vhtfm.session.user;

	let user_info;
	if (!(vhtfm.boot.user_info && vhtfm.boot.user_info[uid])) {
		user_info = { fullname: uid || "Unknown" };
	} else {
		user_info = vhtfm.boot.user_info[uid];
	}

	user_info.abbr = vhtfm.get_abbr(user_info.fullname);
	user_info.color = vhtfm.get_palette(user_info.fullname);

	return user_info;
};

vhtfm.update_user_info = function (user_info) {
	for (let user in user_info) {
		if (vhtfm.boot.user_info[user]) {
			Object.assign(vhtfm.boot.user_info[user], user_info[user]);
		} else {
			vhtfm.boot.user_info[user] = user_info[user];
		}
	}
};

vhtfm.provide("vhtfm.user");

$.extend(vhtfm.user, {
	name: "Guest",
	full_name: function (uid) {
		return uid === vhtfm.session.user
			? __(
					"You",
					null,
					"Name of the current user. For example: You edited this 5 hours ago."
			  )
			: vhtfm.user_info(uid).fullname;
	},
	image: function (uid) {
		return vhtfm.user_info(uid).image;
	},
	abbr: function (uid) {
		return vhtfm.user_info(uid).abbr;
	},
	has_role: function (rl) {
		if (typeof rl == "string") rl = [rl];
		for (var i in rl) {
			if ((vhtfm.boot ? vhtfm.boot.user.roles : ["Guest"]).indexOf(rl[i]) != -1)
				return true;
		}
	},
	get_desktop_items: function () {
		// hide based on permission
		var modules_list = $.map(vhtfm.boot.allowed_modules, function (icon) {
			var m = icon.module_name;
			var type = vhtfm.modules[m] && vhtfm.modules[m].type;

			if (vhtfm.boot.user.allow_modules.indexOf(m) === -1) return null;

			var ret = null;
			if (type === "module") {
				if (vhtfm.boot.user.allow_modules.indexOf(m) != -1 || vhtfm.modules[m].is_help)
					ret = m;
			} else if (type === "page") {
				if (vhtfm.boot.allowed_pages.indexOf(vhtfm.modules[m].link) != -1) ret = m;
			} else if (type === "list") {
				if (vhtfm.model.can_read(vhtfm.modules[m]._doctype)) ret = m;
			} else if (type === "view") {
				ret = m;
			} else if (type === "setup") {
				if (
					vhtfm.user.has_role("System Manager") ||
					vhtfm.user.has_role("Administrator")
				)
					ret = m;
			} else {
				ret = m;
			}

			return ret;
		});

		return modules_list;
	},

	is_report_manager: function () {
		return vhtfm.user.has_role(["Administrator", "System Manager", "Report Manager"]);
	},

	get_formatted_email: function (email) {
		var fullname = vhtfm.user.full_name(email);

		if (!fullname) {
			return email;
		} else {
			// to quote or to not
			var quote = "";

			// only if these special characters are found
			// why? To make the output same as that in python!
			if (fullname.search(/[\[\]\\()<>@,:;".]/) !== -1) {
				quote = '"';
			}

			return repl("%(quote)s%(fullname)s%(quote)s <%(email)s>", {
				fullname: fullname,
				email: email,
				quote: quote,
			});
		}
	},

	get_emails: () => {
		return Object.keys(vhtfm.boot.user_info).map((key) => vhtfm.boot.user_info[key].email);
	},

	/* Normally vhtfm.user is an object
	 * having properties and methods.
	 * But in the following case
	 *
	 * if (vhtfm.user === 'Administrator')
	 *
	 * vhtfm.user will cast to a string
	 * returning vhtfm.user.name
	 */
	toString: function () {
		return this.name;
	},
});

vhtfm.session_alive = true;
$(document).bind("mousemove", function () {
	if (vhtfm.session_alive === false) {
		$(document).trigger("session_alive");
	}
	vhtfm.session_alive = true;
	if (vhtfm.session_alive_timeout) clearTimeout(vhtfm.session_alive_timeout);
	vhtfm.session_alive_timeout = setTimeout("vhtfm.session_alive=false;", 30000);
});
