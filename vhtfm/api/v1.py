import json

from werkzeug.routing import Rule

import vhtfm
from vhtfm import _
from vhtfm.utils.data import sbool


def document_list(doctype: str):
	if vhtfm.form_dict.get("fields"):
		vhtfm.form_dict["fields"] = json.loads(vhtfm.form_dict["fields"])

	# set limit of records for vhtfm.get_list
	vhtfm.form_dict.setdefault(
		"limit_page_length",
		vhtfm.form_dict.limit or vhtfm.form_dict.limit_page_length or 20,
	)

	# convert strings to native types - only as_dict and debug accept bool
	for param in ["as_dict", "debug"]:
		param_val = vhtfm.form_dict.get(param)
		if param_val is not None:
			vhtfm.form_dict[param] = sbool(param_val)

	# evaluate vhtfm.get_list
	return vhtfm.call(vhtfm.client.get_list, doctype, **vhtfm.form_dict)


def handle_rpc_call(method: str):
	import vhtfm.handler

	method = method.split("/")[0]  # for backward compatiblity

	vhtfm.form_dict.cmd = method
	return vhtfm.handler.handle()


def create_doc(doctype: str):
	data = get_request_form_data()
	data.pop("doctype", None)
	return vhtfm.new_doc(doctype, **data).insert()


def update_doc(doctype: str, name: str):
	data = get_request_form_data()

	doc = vhtfm.get_doc(doctype, name, for_update=True)
	if "flags" in data:
		del data["flags"]

	doc.update(data)
	doc.save()

	# check for child table doctype
	if doc.get("parenttype"):
		vhtfm.get_doc(doc.parenttype, doc.parent).save()

	return doc


def delete_doc(doctype: str, name: str):
	# TODO: child doc handling
	vhtfm.delete_doc(doctype, name, ignore_missing=False)
	vhtfm.response.http_status_code = 202
	return "ok"


def read_doc(doctype: str, name: str):
	# Backward compatiblity
	if "run_method" in vhtfm.form_dict:
		return execute_doc_method(doctype, name)

	doc = vhtfm.get_doc(doctype, name)
	doc.check_permission("read")
	doc.apply_fieldlevel_read_permissions()
	return doc


def execute_doc_method(doctype: str, name: str, method: str | None = None):
	method = method or vhtfm.form_dict.pop("run_method")
	doc = vhtfm.get_doc(doctype, name)
	doc.is_whitelisted(method)

	if vhtfm.request.method == "GET":
		doc.check_permission("read")
		return doc.run_method(method, **vhtfm.form_dict)

	elif vhtfm.request.method == "POST":
		doc.check_permission("write")
		return doc.run_method(method, **vhtfm.form_dict)


def get_request_form_data():
	if vhtfm.form_dict.data is None:
		data = vhtfm.safe_decode(vhtfm.request.get_data())
	else:
		data = vhtfm.form_dict.data

	try:
		return vhtfm.parse_json(data)
	except ValueError:
		return vhtfm.form_dict


url_rules = [
	Rule("/method/<path:method>", endpoint=handle_rpc_call),
	Rule("/resource/<doctype>", methods=["GET"], endpoint=document_list),
	Rule("/resource/<doctype>", methods=["POST"], endpoint=create_doc),
	Rule("/resource/<doctype>/<path:name>/", methods=["GET"], endpoint=read_doc),
	Rule("/resource/<doctype>/<path:name>/", methods=["PUT"], endpoint=update_doc),
	Rule("/resource/<doctype>/<path:name>/", methods=["DELETE"], endpoint=delete_doc),
	Rule("/resource/<doctype>/<path:name>/", methods=["POST"], endpoint=execute_doc_method),
]
