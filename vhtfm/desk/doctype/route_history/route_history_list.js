vhtfm.listview_settings["Route History"] = {
	onload: function (listview) {
		vhtfm.require("logtypes.bundle.js", () => {
			vhtfm.utils.logtypes.show_log_retention_message(cur_list.doctype);
		});
	},
};
