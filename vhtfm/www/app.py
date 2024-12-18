# Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import os

no_cache = 1

import json
import re
from urllib.parse import urlencode

import vhtfm
import vhtfm.sessions
from vhtfm import _
from vhtfm.utils.jinja_globals import is_rtl

SCRIPT_TAG_PATTERN = re.compile(r"\<script[^<]*\</script\>")
CLOSING_SCRIPT_TAG_PATTERN = re.compile(r"</script\>")


def get_context(context):
	if vhtfm.session.user == "Guest":
		vhtfm.response["status_code"] = 403
		vhtfm.msgprint(_("Log in to access this page."))
		vhtfm.redirect(f"/login?{urlencode({'redirect-to': vhtfm.request.path})}")

	elif vhtfm.db.get_value("User", vhtfm.session.user, "user_type", order_by=None) == "Website User":
		vhtfm.throw(_("You are not permitted to access this page."), vhtfm.PermissionError)

	try:
		boot = vhtfm.sessions.get()
	except Exception as e:
		raise vhtfm.SessionBootFailed from e

	# this needs commit
	csrf_token = vhtfm.sessions.get_csrf_token()

	vhtfm.db.commit()

	boot_json = vhtfm.as_json(boot, indent=None, separators=(",", ":"))

	# remove script tags from boot
	boot_json = SCRIPT_TAG_PATTERN.sub("", boot_json)

	# TODO: Find better fix
	boot_json = CLOSING_SCRIPT_TAG_PATTERN.sub("", boot_json)

	hooks = vhtfm.get_hooks()
	app_include_js = hooks.get("app_include_js", []) + vhtfm.conf.get("app_include_js", [])
	app_include_css = hooks.get("app_include_css", []) + vhtfm.conf.get("app_include_css", [])
	app_include_icons = hooks.get("app_include_icons", [])

	if vhtfm.get_system_settings("enable_telemetry") and os.getenv("VHTFM_SENTRY_DSN"):
		app_include_js.append("sentry.bundle.js")

	context.update(
		{
			"no_cache": 1,
			"build_version": vhtfm.utils.get_build_version(),
			"app_include_js": app_include_js,
			"app_include_css": app_include_css,
			"app_include_icons": app_include_icons,
			"layout_direction": "rtl" if is_rtl() else "ltr",
			"lang": vhtfm.local.lang,
			"sounds": hooks["sounds"],
			"boot": boot if context.get("for_mobile") else json.loads(boot_json),
			"desk_theme": boot.get("desk_theme") or "Light",
			"csrf_token": csrf_token,
			"google_analytics_id": vhtfm.conf.get("google_analytics_id"),
			"google_analytics_anonymize_ip": vhtfm.conf.get("google_analytics_anonymize_ip"),
			"app_name": (
				vhtfm.get_website_settings("app_name") or vhtfm.get_system_settings("app_name") or "Vhtfm"
			),
		}
	)

	return context
