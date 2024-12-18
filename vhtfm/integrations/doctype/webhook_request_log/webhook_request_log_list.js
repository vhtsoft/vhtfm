vhtfm.listview_settings["Webhook Request Log"] = {
	onload: function (list_view) {
		vhtfm.require("logtypes.bundle.js", () => {
			vhtfm.utils.logtypes.show_log_retention_message(list_view.doctype);
		});
	},
};
