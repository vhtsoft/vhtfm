# Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE


from urllib.parse import urlparse

import vhtfm
import vhtfm.utils
from vhtfm import _
from vhtfm.apps import get_default_path
from vhtfm.auth import LoginManager
from vhtfm.core.doctype.navbar_settings.navbar_settings import get_app_logo
from vhtfm.rate_limiter import rate_limit
from vhtfm.utils import cint, get_url
from vhtfm.utils.data import escape_html
from vhtfm.utils.html_utils import get_icon_html
from vhtfm.utils.jinja import guess_is_path
from vhtfm.utils.oauth import get_oauth2_authorize_url, get_oauth_keys, redirect_post_login
from vhtfm.utils.password import get_decrypted_password
from vhtfm.website.utils import get_home_page

no_cache = True


def get_context(context):
	redirect_to = vhtfm.local.request.args.get("redirect-to")
	redirect_to = sanitize_redirect(redirect_to)

	if vhtfm.session.user != "Guest":
		if not redirect_to:
			if vhtfm.session.data.user_type == "Website User":
				redirect_to = get_default_path() or get_home_page()
			else:
				redirect_to = get_default_path() or "/app"

		if redirect_to != "login":
			vhtfm.local.flags.redirect_location = redirect_to
			raise vhtfm.Redirect

	context.no_header = True
	context.for_test = "login.html"
	context["title"] = "Login"
	context["hide_login"] = True  # dont show login link on login page again.
	context["provider_logins"] = []
	context["disable_signup"] = cint(vhtfm.get_website_settings("disable_signup"))
	context["show_footer_on_login"] = cint(vhtfm.get_website_settings("show_footer_on_login"))
	context["disable_user_pass_login"] = cint(vhtfm.get_system_settings("disable_user_pass_login"))
	context["logo"] = get_app_logo()
	context["app_name"] = (
		vhtfm.get_website_settings("app_name") or vhtfm.get_system_settings("app_name") or _("Vhtfm")
	)

	signup_form_template = vhtfm.get_hooks("signup_form_template")
	if signup_form_template and len(signup_form_template):
		path = signup_form_template[-1]
		if not guess_is_path(path):
			path = vhtfm.get_attr(signup_form_template[-1])()
	else:
		path = "vhtfm/templates/signup.html"

	if path:
		context["signup_form_template"] = vhtfm.get_template(path).render()

	providers = vhtfm.get_all(
		"Social Login Key",
		filters={"enable_social_login": 1},
		fields=["name", "client_id", "base_url", "provider_name", "icon"],
		order_by="name",
	)

	for provider in providers:
		client_secret = get_decrypted_password(
			"Social Login Key", provider.name, "client_secret", raise_exception=False
		)
		if not client_secret:
			continue

		icon = None
		if provider.icon:
			if provider.provider_name == "Custom":
				icon = get_icon_html(provider.icon, small=True)
			else:
				icon = f"<img src={escape_html(provider.icon)!r} alt={escape_html(provider.provider_name)!r}>"

		if provider.client_id and provider.base_url and get_oauth_keys(provider.name):
			context.provider_logins.append(
				{
					"name": provider.name,
					"provider_name": provider.provider_name,
					"auth_url": get_oauth2_authorize_url(provider.name, redirect_to),
					"icon": icon,
				}
			)
			context["social_login"] = True

	if cint(vhtfm.db.get_value("LDAP Settings", "LDAP Settings", "enabled")):
		from vhtfm.integrations.doctype.ldap_settings.ldap_settings import LDAPSettings

		context["ldap_settings"] = LDAPSettings.get_ldap_client_settings()

	login_label = [_("Email")]

	if vhtfm.utils.cint(vhtfm.get_system_settings("allow_login_using_mobile_number")):
		login_label.append(_("Mobile"))

	if vhtfm.utils.cint(vhtfm.get_system_settings("allow_login_using_user_name")):
		login_label.append(_("Username"))

	context["login_label"] = f" {_('or')} ".join(login_label)

	context["login_with_email_link"] = vhtfm.get_system_settings("login_with_email_link")

	return context


@vhtfm.whitelist(allow_guest=True)
def login_via_token(login_token: str):
	sid = vhtfm.cache.get_value(f"login_token:{login_token}", expires=True)
	if not sid:
		vhtfm.respond_as_web_page(_("Invalid Request"), _("Invalid Login Token"), http_status_code=417)
		return

	vhtfm.local.form_dict.sid = sid
	vhtfm.local.login_manager = LoginManager()

	redirect_post_login(
		desk_user=vhtfm.db.get_value("User", vhtfm.session.user, "user_type") == "System User"
	)


@vhtfm.whitelist(allow_guest=True)
@rate_limit(limit=5, seconds=60 * 60)
def send_login_link(email: str):
	if not vhtfm.get_system_settings("login_with_email_link"):
		return

	expiry = vhtfm.get_system_settings("login_with_email_link_expiry") or 10
	link = _generate_temporary_login_link(email, expiry)

	app_name = (
		vhtfm.get_website_settings("app_name") or vhtfm.get_system_settings("app_name") or _("Vhtfm")
	)

	subject = _("Login To {0}").format(app_name)

	vhtfm.sendmail(
		subject=subject,
		recipients=email,
		template="login_with_email_link",
		args={"link": link, "minutes": expiry, "app_name": app_name},
		now=True,
	)


def _generate_temporary_login_link(email: str, expiry: int):
	assert isinstance(email, str)

	if not vhtfm.db.exists("User", email):
		vhtfm.throw(_("User with email address {0} does not exist").format(email), vhtfm.DoesNotExistError)
	key = vhtfm.generate_hash()
	vhtfm.cache.set_value(f"one_time_login_key:{key}", email, expires_in_sec=expiry * 60)

	return get_url(f"/api/method/vhtfm.www.login.login_via_key?key={key}")


def get_login_with_email_link_ratelimit() -> int:
	return vhtfm.get_system_settings("rate_limit_email_link_login") or 5


@vhtfm.whitelist(allow_guest=True, methods=["GET"])
@rate_limit(limit=get_login_with_email_link_ratelimit, seconds=60 * 60)
def login_via_key(key: str):
	cache_key = f"one_time_login_key:{key}"
	email = vhtfm.cache.get_value(cache_key)

	if email:
		vhtfm.cache.delete_value(cache_key)
		vhtfm.local.login_manager.login_as(email)

		redirect_post_login(
			desk_user=vhtfm.db.get_value("User", vhtfm.session.user, "user_type") == "System User"
		)
	else:
		vhtfm.respond_as_web_page(
			_("Not Permitted"),
			_("The link you trying to login is invalid or expired."),
			http_status_code=403,
			indicator_color="red",
		)


def sanitize_redirect(redirect: str | None) -> str | None:
	"""Only allow redirect on same domain.

	Allowed redirects:
	- Same host e.g. https://vhtfm.localhost/path
	- Just path e.g. /app
	"""
	if not redirect:
		return redirect

	parsed_redirect = urlparse(redirect)
	if not parsed_redirect.netloc:
		return redirect

	parsed_request_host = urlparse(vhtfm.local.request.url)
	if parsed_request_host.netloc == parsed_redirect.netloc:
		return redirect

	return None
