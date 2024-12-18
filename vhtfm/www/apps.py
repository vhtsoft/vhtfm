# Copyright (c) 2023, Vhtfm Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

import vhtfm
from vhtfm import _
from vhtfm.apps import get_apps


def get_context():
	all_apps = get_apps()

	system_default_app = vhtfm.get_system_settings("default_app")
	user_default_app = vhtfm.db.get_value("User", vhtfm.session.user, "default_app")
	default_app = user_default_app if user_default_app else system_default_app

	if len(all_apps) == 0:
		vhtfm.local.flags.redirect_location = "/app"
		raise vhtfm.Redirect

	for app in all_apps:
		app["is_default"] = True if app.get("name") == default_app else False

	return {"apps": all_apps}
