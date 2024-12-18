# Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

from urllib.parse import parse_qsl

import vhtfm
from vhtfm import _
from vhtfm.twofactor import get_qr_svg_code


def get_context(context):
	context.no_cache = 1
	context.qr_code_user, context.qrcode_svg = get_user_svg_from_cache()


def get_query_key():
	"""Return query string arg."""
	query_string = vhtfm.local.request.query_string
	query = dict(parse_qsl(query_string))
	query = {key.decode(): val.decode() for key, val in query.items()}
	if "k" not in list(query):
		vhtfm.throw(_("Not Permitted"), vhtfm.PermissionError)
	query = (query["k"]).strip()
	if False in [i.isalpha() or i.isdigit() for i in query]:
		vhtfm.throw(_("Not Permitted"), vhtfm.PermissionError)
	return query


def get_user_svg_from_cache():
	"""Get User and SVG code from cache."""
	key = get_query_key()
	totp_uri = vhtfm.cache.get_value(f"{key}_uri")
	user = vhtfm.cache.get_value(f"{key}_user")
	if not totp_uri or not user:
		vhtfm.throw(_("Page has expired!"), vhtfm.PermissionError)
	if not vhtfm.db.exists("User", user):
		vhtfm.throw(_("Not Permitted"), vhtfm.PermissionError)
	user = vhtfm.get_doc("User", user)
	svg = get_qr_svg_code(totp_uri)
	return (user, svg.decode())
