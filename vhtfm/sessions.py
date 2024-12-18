# Copyright (c) 2021, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
"""
Boot session from cache or build

Session bootstraps info needed by common client side activities including
permission, homepage, default variables, system defaults etc
"""

import json
from urllib.parse import unquote

import redis

import vhtfm
import vhtfm.defaults
import vhtfm.model.meta
import vhtfm.translate
import vhtfm.utils
from vhtfm import _
from vhtfm.apps import get_apps, get_default_path, is_desk_apps
from vhtfm.cache_manager import clear_user_cache
from vhtfm.query_builder import Order
from vhtfm.utils import cint, cstr, get_assets_json
from vhtfm.utils.change_log import has_app_update_notifications
from vhtfm.utils.data import add_to_date


@vhtfm.whitelist()
def clear():
	vhtfm.local.session_obj.update(force=True)
	vhtfm.local.db.commit()
	clear_user_cache(vhtfm.session.user)
	vhtfm.response["message"] = _("Cache Cleared")


def clear_sessions(user=None, keep_current=False, force=False):
	"""Clear other sessions of the current user. Called at login / logout

	:param user: user name (default: current user)
	:param keep_current: keep current session (default: false)
	:param force: triggered by the user (default false)
	"""

	reason = "Logged In From Another Session"
	if force:
		reason = "Force Logged out by the user"

	for sid in get_sessions_to_clear(user, keep_current, force):
		delete_session(sid, reason=reason)


def get_sessions_to_clear(user=None, keep_current=False, force=False):
	"""Return sessions of the current user. Called at login / logout.

	:param user: user name (default: current user)
	:param keep_current: keep current session (default: false)
	:param force: ignore simultaneous sessions count, log the user out of all except current (default: false)
	"""
	if not user:
		user = vhtfm.session.user

	offset = 0
	if not force and user == vhtfm.session.user:
		simultaneous_sessions = vhtfm.db.get_value("User", user, "simultaneous_sessions") or 1
		offset = simultaneous_sessions

	session = vhtfm.qb.DocType("Sessions")
	session_id = vhtfm.qb.from_(session).where(session.user == user)
	if keep_current:
		if not force:
			offset = max(0, offset - 1)
		session_id = session_id.where(session.sid != vhtfm.session.sid)

	query = (
		session_id.select(session.sid).offset(offset).limit(100).orderby(session.lastupdate, order=Order.desc)
	)

	return query.run(pluck=True)


def delete_session(sid=None, user=None, reason="Session Expired"):
	from vhtfm.core.doctype.activity_log.feed import logout_feed

	if vhtfm.flags.read_only:
		# This isn't manually initiated logout, most likely user's cookies were expired in such case
		# we should just ignore it till database is back up again.
		return

	if sid and not user:
		table = vhtfm.qb.DocType("Sessions")
		user_details = vhtfm.qb.from_(table).where(table.sid == sid).select(table.user).run(as_dict=True)
		if user_details:
			user = user_details[0].get("user")

	logout_feed(user, reason)
	vhtfm.db.delete("Sessions", {"sid": sid})
	vhtfm.db.commit()

	vhtfm.cache.hdel("session", sid)
	vhtfm.cache.hdel("last_db_session_update", sid)


def clear_all_sessions(reason=None):
	"""This effectively logs out all users"""
	vhtfm.only_for("Administrator")
	if not reason:
		reason = "Deleted All Active Session"
	for sid in vhtfm.qb.from_("Sessions").select("sid").run(pluck=True):
		delete_session(sid, reason=reason)


def get_expired_sessions():
	"""Return list of expired sessions."""

	sessions = vhtfm.qb.DocType("Sessions")
	return (
		vhtfm.qb.from_(sessions).select(sessions.sid).where(sessions.lastupdate < get_expired_threshold())
	).run(pluck=True)


def clear_expired_sessions():
	"""This function is meant to be called from scheduler"""
	for sid in get_expired_sessions():
		delete_session(sid, reason="Session Expired")


def get():
	"""get session boot info"""
	from vhtfm.boot import get_bootinfo, get_unseen_notes
	from vhtfm.utils.change_log import get_change_log

	bootinfo = None
	if not getattr(vhtfm.conf, "disable_session_cache", None):
		# check if cache exists
		bootinfo = vhtfm.cache.hget("bootinfo", vhtfm.session.user)
		if bootinfo:
			bootinfo["from_cache"] = 1
			bootinfo["user"]["recent"] = json.dumps(vhtfm.cache.hget("user_recent", vhtfm.session.user))

	if not bootinfo:
		# if not create it
		bootinfo = get_bootinfo()
		vhtfm.cache.hset("bootinfo", vhtfm.session.user, bootinfo)
		try:
			vhtfm.cache.ping()
		except redis.exceptions.ConnectionError:
			message = _("Redis cache server not running. Please contact Administrator / Tech support")
			if "messages" in bootinfo:
				bootinfo["messages"].append(message)
			else:
				bootinfo["messages"] = [message]

		# check only when clear cache is done, and don't cache this
		if vhtfm.local.request:
			bootinfo["change_log"] = get_change_log()

	bootinfo["metadata_version"] = vhtfm.cache.get_value("metadata_version")
	if not bootinfo["metadata_version"]:
		bootinfo["metadata_version"] = vhtfm.reset_metadata_version()

	bootinfo.notes = get_unseen_notes()
	bootinfo.assets_json = get_assets_json()
	bootinfo.read_only = bool(vhtfm.flags.read_only)

	for hook in vhtfm.get_hooks("extend_bootinfo"):
		vhtfm.get_attr(hook)(bootinfo=bootinfo)

	bootinfo["lang"] = vhtfm.translate.get_user_lang()
	bootinfo["disable_async"] = vhtfm.conf.disable_async

	bootinfo["setup_complete"] = cint(vhtfm.get_system_settings("setup_complete"))
	bootinfo["apps_data"] = {
		"apps": get_apps() or [],
		"is_desk_apps": 1 if bool(is_desk_apps(get_apps())) else 0,
		"default_path": get_default_path() or "",
	}

	bootinfo["desk_theme"] = vhtfm.db.get_value("User", vhtfm.session.user, "desk_theme") or "Light"
	bootinfo["user"]["impersonated_by"] = vhtfm.session.data.get("impersonated_by")
	bootinfo["navbar_settings"] = vhtfm.get_cached_doc("Navbar Settings")
	bootinfo.has_app_updates = has_app_update_notifications()

	return bootinfo


@vhtfm.whitelist()
def get_boot_assets_json():
	return get_assets_json()


def get_csrf_token():
	if not vhtfm.local.session.data.csrf_token:
		generate_csrf_token()

	return vhtfm.local.session.data.csrf_token


def generate_csrf_token():
	vhtfm.local.session.data.csrf_token = vhtfm.generate_hash()
	if not vhtfm.flags.in_test:
		vhtfm.local.session_obj.update(force=True)


class Session:
	__slots__ = ("_update_in_cache", "data", "full_name", "sid", "time_diff", "user", "user_type")

	def __init__(self, user, resume=False, full_name=None, user_type=None):
		self.sid = cstr(vhtfm.form_dict.get("sid") or unquote(vhtfm.request.cookies.get("sid", "Guest")))
		self.user = user
		self.user_type = user_type
		self.full_name = full_name
		self.data = vhtfm._dict({"data": vhtfm._dict({})})
		self.time_diff = None
		self._update_in_cache = False

		# set local session
		vhtfm.local.session = self.data

		if resume:
			self.resume()

		else:
			if self.user:
				self.validate_user()
				self.start()

	def validate_user(self):
		if not vhtfm.get_cached_value("User", self.user, "enabled"):
			vhtfm.throw(
				_("User {0} is disabled. Please contact your System Manager.").format(self.user),
				vhtfm.ValidationError,
			)

	def start(self):
		"""start a new session"""
		# generate sid
		if self.user == "Guest":
			sid = "Guest"
		else:
			sid = vhtfm.generate_hash()

		self.data.user = self.user
		self.sid = self.data.sid = sid
		self.data.data.user = self.user
		self.data.data.session_ip = vhtfm.local.request_ip
		if self.user != "Guest":
			self.data.data.update(
				{
					"last_updated": vhtfm.utils.now(),
					"session_expiry": get_expiry_period(),
					"full_name": self.full_name,
					"user_type": self.user_type,
				}
			)

		# insert session
		if self.user != "Guest":
			self.insert_session_record()

			# update user
			user = vhtfm.get_doc("User", self.data["user"])
			user_doctype = vhtfm.qb.DocType("User")
			(
				vhtfm.qb.update(user_doctype)
				.set(user_doctype.last_login, vhtfm.utils.now())
				.set(user_doctype.last_ip, vhtfm.local.request_ip)
				.set(user_doctype.last_active, vhtfm.utils.now())
				.where(user_doctype.name == self.data["user"])
			).run()

			user.run_notifications("before_change")
			user.run_notifications("on_update")
			vhtfm.db.commit()

	def insert_session_record(self):
		Sessions = vhtfm.qb.DocType("Sessions")
		now = vhtfm.utils.now()

		(
			vhtfm.qb.into(Sessions)
			.columns(Sessions.sessiondata, Sessions.user, Sessions.lastupdate, Sessions.sid, Sessions.status)
			.insert(
				(
					vhtfm.as_json(self.data["data"], indent=None, separators=(",", ":")),
					self.data["user"],
					now,
					self.data["sid"],
					"Active",
				)
			)
		).run()
		vhtfm.cache.hset("session", self.data.sid, self.data)

	def resume(self):
		"""non-login request: load a session"""
		import vhtfm
		from vhtfm.auth import validate_ip_address

		data = self.get_session_record()

		if data:
			self.data.update({"data": data, "user": data.user, "sid": self.sid})
			self.user = data.user
			self.validate_user()
			validate_ip_address(self.user)
		else:
			self.start_as_guest()

		if self.sid != "Guest":
			vhtfm.local.user_lang = vhtfm.translate.get_user_lang(self.data.user)
			vhtfm.local.lang = vhtfm.local.user_lang

	def get_session_record(self):
		"""get session record, or return the standard Guest Record"""
		from vhtfm.auth import clear_cookies

		r = self.get_session_data()

		if not r:
			vhtfm.response["session_expired"] = 1
			clear_cookies()
			self.sid = "Guest"
			r = self.get_session_data()

		return r

	def get_session_data(self):
		if self.sid == "Guest":
			return vhtfm._dict({"user": "Guest"})

		data = self.get_session_data_from_cache()
		if not data:
			self._update_in_cache = True
			data = self.get_session_data_from_db()
		return data

	def get_session_data_from_cache(self):
		data = vhtfm.cache.hget("session", self.sid)
		if data:
			data = vhtfm._dict(data)
			session_data = data.get("data", {})

			# set user for correct timezone
			self.time_diff = vhtfm.utils.time_diff_in_seconds(
				vhtfm.utils.now(), session_data.get("last_updated")
			)
			expiry = get_expiry_in_seconds(session_data.get("session_expiry"))

			if self.time_diff > expiry:
				self._delete_session()
				data = None

		return data and data.data

	def get_session_data_from_db(self):
		sessions = vhtfm.qb.DocType("Sessions")

		record = (
			vhtfm.qb.from_(sessions)
			.select(sessions.user, sessions.sessiondata)
			.where(sessions.sid == self.sid)
			.where(sessions.lastupdate > get_expired_threshold())
		).run()

		if record:
			data = vhtfm.parse_json(record[0][1] or "{}")
			data.user = record[0][0]
		else:
			self._delete_session()
			data = None

		return data

	def _delete_session(self):
		delete_session(self.sid, reason="Session Expired")

	def start_as_guest(self):
		"""all guests share the same 'Guest' session"""
		self.user = "Guest"
		self.start()

	def update(self, force=False):
		"""extend session expiry"""

		if vhtfm.session.user == "Guest":
			return

		now = vhtfm.utils.now()

		Sessions = vhtfm.qb.DocType("Sessions")

		# update session in db
		last_updated = vhtfm.cache.hget("last_db_session_update", self.sid)
		time_diff = vhtfm.utils.time_diff_in_seconds(now, last_updated) if last_updated else None

		# database persistence is secondary, don't update it too often
		updated_in_db = False
		if (force or (time_diff is None) or (time_diff > 600)) and not vhtfm.flags.read_only:
			self.data.data.last_updated = now
			self.data.data.lang = str(vhtfm.lang)
			# update sessions table
			(
				vhtfm.qb.update(Sessions)
				.where(Sessions.sid == self.data["sid"])
				.set(
					Sessions.sessiondata,
					vhtfm.as_json(self.data["data"], indent=None, separators=(",", ":")),
				)
				.set(Sessions.lastupdate, now)
			).run()

			vhtfm.db.set_value("User", vhtfm.session.user, "last_active", now, update_modified=False)

			vhtfm.db.commit()
			updated_in_db = True

			vhtfm.cache.hset("last_db_session_update", self.sid, now)
			vhtfm.cache.hset("session", self.sid, self.data)

		return updated_in_db

	def set_impersonsated(self, original_user):
		self.data.data.impersonated_by = original_user
		# Forcefully flush session
		self.update(force=True)


def get_expiry_period_for_query():
	if vhtfm.db.db_type == "postgres":
		return get_expiry_period()
	else:
		return get_expiry_in_seconds()


def get_expiry_in_seconds(expiry=None):
	if not expiry:
		expiry = get_expiry_period()

	parts = expiry.split(":")
	return (cint(parts[0]) * 3600) + (cint(parts[1]) * 60) + cint(parts[2])


def get_expired_threshold():
	"""Get cutoff time before which all sessions are considered expired."""

	now = vhtfm.utils.now()
	expiry_in_seconds = get_expiry_in_seconds()

	return add_to_date(now, seconds=-expiry_in_seconds, as_string=True)


def get_expiry_period():
	exp_sec = vhtfm.defaults.get_global_default("session_expiry") or "240:00:00"

	# incase seconds is missing
	if len(exp_sec.split(":")) == 2:
		exp_sec = exp_sec + ":00"

	return exp_sec


def get_geo_from_ip(ip_addr):
	try:
		from geolite2 import geolite2

		with geolite2 as f:
			reader = f.reader()
			data = reader.get(ip_addr)

			return vhtfm._dict(data)
	except ImportError:
		return
	except ValueError:
		return
	except TypeError:
		return


def get_geo_ip_country(ip_addr):
	match = get_geo_from_ip(ip_addr)
	if match:
		return match.country
