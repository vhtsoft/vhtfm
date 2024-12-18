vhtfm.listview_settings["Prepared Report"] = {
	onload: function (list_view) {
		vhtfm.require("logtypes.bundle.js", () => {
			vhtfm.utils.logtypes.show_log_retention_message(list_view.doctype);
		});
	},
};
