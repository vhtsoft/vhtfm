vhtfm.pages["user-profile"].on_page_load = function (wrapper) {
	vhtfm.require("user_profile_controller.bundle.js", () => {
		let user_profile = new vhtfm.ui.UserProfile(wrapper);
		user_profile.show();
	});
};
