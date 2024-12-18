"""REST API v2

This file defines routes and implementation for REST API.

Note:
	- All functions in this file should be treated as "whitelisted" as they are exposed via routes
	- None of the functions present here should be called from python code, their location and
	  internal implementation can change without treating it as "breaking change".
"""

import json
from typing import Any

from werkzeug.routing import Rule

import vhtfm
import vhtfm.client
from vhtfm import _, get_newargs, is_whitelisted
from vhtfm.core.doctype.server_script.server_script_utils import get_server_script_map
from vhtfm.handler import is_valid_http_method, run_server_script, upload_file

PERMISSION_MAP = {
	"GET": "read",
	"POST": "write",
}


def handle_rpc_call(method: str, doctype: str | None = None):
	from vhtfm.modules.utils import load_doctype_module

	if doctype:
		# Expand to run actual method from doctype controller
		module = load_doctype_module(doctype)
		method = module.__name__ + "." + method

	for hook in reversed(vhtfm.get_hooks("override_whitelisted_methods", {}).get(method, [])):
		# override using the last hook
		method = hook
		break

	# via server script
	server_script = get_server_script_map().get("_api", {}).get(method)
	if server_script:
		return run_server_script(server_script)

	try:
		method = vhtfm.get_attr(method)
	except Exception as e:
		vhtfm.throw(_("Failed to get method {0} with {1}").format(method, e))

	is_whitelisted(method)
	is_valid_http_method(method)

	return vhtfm.call(method, **vhtfm.form_dict)


def login():
	"""Login happens implicitly, this function doesn't do anything."""
	pass


def logout():
	vhtfm.local.login_manager.logout()
	vhtfm.db.commit()


def read_doc(doctype: str, name: str):
	doc = vhtfm.get_doc(doctype, name)
	doc.check_permission("read")
	doc.apply_fieldlevel_read_permissions()
	return doc


def document_list(doctype: str):
	if vhtfm.form_dict.get("fields"):
		vhtfm.form_dict["fields"] = json.loads(vhtfm.form_dict["fields"])

	# set limit of records for vhtfm.get_list
	vhtfm.form_dict.limit_page_length = vhtfm.form_dict.limit or 20
	# evaluate vhtfm.get_list
	return vhtfm.call(vhtfm.client.get_list, doctype, **vhtfm.form_dict)


def count(doctype: str) -> int:
	from vhtfm.desk.reportview import get_count

	vhtfm.form_dict.doctype = doctype

	return get_count()


def create_doc(doctype: str):
	data = vhtfm.form_dict
	data.pop("doctype", None)
	return vhtfm.new_doc(doctype, **data).insert()


def update_doc(doctype: str, name: str):
	data = vhtfm.form_dict

	doc = vhtfm.get_doc(doctype, name, for_update=True)
	data.pop("flags", None)
	doc.update(data)
	doc.save()

	# check for child table doctype
	if doc.get("parenttype"):
		vhtfm.get_doc(doc.parenttype, doc.parent).save()

	return doc


def delete_doc(doctype: str, name: str):
	vhtfm.client.delete_doc(doctype, name)
	vhtfm.response.http_status_code = 202
	return "ok"


def get_meta(doctype: str):
	vhtfm.only_for("All")
	return vhtfm.get_meta(doctype)


def execute_doc_method(doctype: str, name: str, method: str | None = None):
	"""Get a document from DB and execute method on it.

	Use cases:
	- Submitting/cancelling document
	- Triggering some kind of update on a document
	"""
	method = method or vhtfm.form_dict.pop("run_method")
	doc = vhtfm.get_doc(doctype, name)
	doc.is_whitelisted(method)

	doc.check_permission(PERMISSION_MAP[vhtfm.request.method])
	return doc.run_method(method, **vhtfm.form_dict)


def run_doc_method(method: str, document: dict[str, Any] | str, kwargs=None):
	"""run a whitelisted controller method on in-memory document.


	This is useful for building clients that don't necessarily encode all the business logic but
	call server side function on object to validate and modify the doc.

	The doc CAN exists in DB too and can write to DB as well if method is POST.
	"""

	if isinstance(document, str):
		document = vhtfm.parse_json(document)

	if kwargs is None:
		kwargs = {}

	doc = vhtfm.get_doc(document)
	doc._original_modified = doc.modified
	doc.check_if_latest()

	doc.check_permission(PERMISSION_MAP[vhtfm.request.method])

	method_obj = getattr(doc, method)
	fn = getattr(method_obj, "__func__", method_obj)
	is_whitelisted(fn)
	is_valid_http_method(fn)

	new_kwargs = get_newargs(fn, kwargs)
	response = doc.run_method(method, **new_kwargs)
	vhtfm.response.docs.append(doc)  # send modified document and result both.
	return response


url_rules = [
	# RPC calls
	Rule("/method/login", endpoint=login),
	Rule("/method/logout", endpoint=logout),
	Rule("/method/ping", endpoint=vhtfm.ping),
	Rule("/method/upload_file", endpoint=upload_file),
	Rule("/method/<method>", endpoint=handle_rpc_call),
	Rule(
		"/method/run_doc_method",
		methods=["GET", "POST"],
		endpoint=lambda: vhtfm.call(run_doc_method, **vhtfm.form_dict),
	),
	Rule("/method/<doctype>/<method>", endpoint=handle_rpc_call),
	# Document level APIs
	Rule("/document/<doctype>", methods=["GET"], endpoint=document_list),
	Rule("/document/<doctype>", methods=["POST"], endpoint=create_doc),
	Rule("/document/<doctype>/<path:name>/", methods=["GET"], endpoint=read_doc),
	Rule("/document/<doctype>/<path:name>/", methods=["PATCH", "PUT"], endpoint=update_doc),
	Rule("/document/<doctype>/<path:name>/", methods=["DELETE"], endpoint=delete_doc),
	Rule(
		"/document/<doctype>/<path:name>/method/<method>/",
		methods=["GET", "POST"],
		endpoint=execute_doc_method,
	),
	# Collection level APIs
	Rule("/doctype/<doctype>/meta", methods=["GET"], endpoint=get_meta),
	Rule("/doctype/<doctype>/count", methods=["GET"], endpoint=count),
]
