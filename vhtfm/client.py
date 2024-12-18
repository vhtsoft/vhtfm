# Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import json
import os
from typing import TYPE_CHECKING

import vhtfm
import vhtfm.model
import vhtfm.utils
from vhtfm import _
from vhtfm.desk.reportview import validate_args
from vhtfm.model.db_query import check_parent_permission
from vhtfm.model.utils import is_virtual_doctype
from vhtfm.utils import get_safe_filters

if TYPE_CHECKING:
	from vhtfm.model.document import Document

"""
Handle RESTful requests that are mapped to the `/api/resource` route.

Requests via VhtfmClient are also handled here.
"""


@vhtfm.whitelist()
def get_list(
	doctype,
	fields=None,
	filters=None,
	group_by=None,
	order_by=None,
	limit_start=None,
	limit_page_length=20,
	parent=None,
	debug: bool = False,
	as_dict: bool = True,
	or_filters=None,
):
	"""Return a list of records by filters, fields, ordering and limit.

	:param doctype: DocType of the data to be queried
	:param fields: fields to be returned. Default is `name`
	:param filters: filter list by this dict
	:param order_by: Order by this fieldname
	:param limit_start: Start at this index
	:param limit_page_length: Number of records to be returned (default 20)"""
	if vhtfm.is_table(doctype):
		check_parent_permission(parent, doctype)

	args = vhtfm._dict(
		doctype=doctype,
		parent_doctype=parent,
		fields=fields,
		filters=filters,
		or_filters=or_filters,
		group_by=group_by,
		order_by=order_by,
		limit_start=limit_start,
		limit_page_length=limit_page_length,
		debug=debug,
		as_list=not as_dict,
	)

	validate_args(args)
	return vhtfm.get_list(**args)


@vhtfm.whitelist()
def get_count(doctype, filters=None, debug=False, cache=False):
	return vhtfm.db.count(doctype, get_safe_filters(filters), debug, cache)


@vhtfm.whitelist()
def get(doctype, name=None, filters=None, parent=None):
	"""Return a document by name or filters.

	:param doctype: DocType of the document to be returned
	:param name: return document of this `name`
	:param filters: If name is not set, filter by these values and return the first match"""
	if vhtfm.is_table(doctype):
		check_parent_permission(parent, doctype)

	if name:
		doc = vhtfm.get_doc(doctype, name)
	elif filters or filters == {}:
		doc = vhtfm.get_doc(doctype, vhtfm.parse_json(filters))
	else:
		doc = vhtfm.get_doc(doctype)  # single

	doc.check_permission()
	doc.apply_fieldlevel_read_permissions()

	return doc.as_dict()


@vhtfm.whitelist()
def get_value(doctype, fieldname, filters=None, as_dict=True, debug=False, parent=None):
	"""Return a value from a document.

	:param doctype: DocType to be queried
	:param fieldname: Field to be returned (default `name`)
	:param filters: dict or string for identifying the record"""
	if vhtfm.is_table(doctype):
		check_parent_permission(parent, doctype)

	if not vhtfm.has_permission(doctype, parent_doctype=parent):
		vhtfm.throw(_("No permission for {0}").format(_(doctype)), vhtfm.PermissionError)

	filters = get_safe_filters(filters)
	if isinstance(filters, str):
		filters = {"name": filters}

	try:
		fields = vhtfm.parse_json(fieldname)
	except (TypeError, ValueError):
		# name passed, not json
		fields = [fieldname]

	# check whether the used filters were really parseable and usable
	# and did not just result in an empty string or dict
	if not filters:
		filters = None

	if vhtfm.get_meta(doctype).issingle:
		value = vhtfm.db.get_values_from_single(fields, filters, doctype, as_dict=as_dict, debug=debug)
	else:
		value = get_list(
			doctype,
			filters=filters,
			fields=fields,
			debug=debug,
			limit_page_length=1,
			parent=parent,
			as_dict=as_dict,
		)

	if as_dict:
		return value[0] if value else {}

	if not value:
		return

	return value[0] if len(fields) > 1 else value[0][0]


@vhtfm.whitelist()
def get_single_value(doctype, field):
	if not vhtfm.has_permission(doctype):
		vhtfm.throw(_("No permission for {0}").format(_(doctype)), vhtfm.PermissionError)

	return vhtfm.db.get_single_value(doctype, field)


@vhtfm.whitelist(methods=["POST", "PUT"])
def set_value(doctype, name, fieldname, value=None):
	"""Set a value using get_doc, group of values

	:param doctype: DocType of the document
	:param name: name of the document
	:param fieldname: fieldname string or JSON / dict with key value pair
	:param value: value if fieldname is JSON / dict"""

	if fieldname in (vhtfm.model.default_fields + vhtfm.model.child_table_fields):
		vhtfm.throw(_("Cannot edit standard fields"))

	if not value:
		values = fieldname
		if isinstance(fieldname, str):
			try:
				values = json.loads(fieldname)
			except ValueError:
				values = {fieldname: ""}
	else:
		values = {fieldname: value}

	# check for child table doctype
	if not vhtfm.get_meta(doctype).istable:
		doc = vhtfm.get_doc(doctype, name)
		doc.update(values)
	else:
		doc = vhtfm.db.get_value(doctype, name, ["parenttype", "parent"], as_dict=True)
		doc = vhtfm.get_doc(doc.parenttype, doc.parent)
		child = doc.getone({"doctype": doctype, "name": name})
		child.update(values)

	doc.save()

	return doc.as_dict()


@vhtfm.whitelist(methods=["POST", "PUT"])
def insert(doc=None):
	"""Insert a document

	:param doc: JSON or dict object to be inserted"""
	if isinstance(doc, str):
		doc = json.loads(doc)

	return insert_doc(doc).as_dict()


@vhtfm.whitelist(methods=["POST", "PUT"])
def insert_many(docs=None):
	"""Insert multiple documents

	:param docs: JSON or list of dict objects to be inserted in one request"""
	if isinstance(docs, str):
		docs = json.loads(docs)

	if len(docs) > 200:
		vhtfm.throw(_("Only 200 inserts allowed in one request"))

	return [insert_doc(doc).name for doc in docs]


@vhtfm.whitelist(methods=["POST", "PUT"])
def save(doc):
	"""Update (save) an existing document

	:param doc: JSON or dict object with the properties of the document to be updated"""
	if isinstance(doc, str):
		doc = json.loads(doc)

	doc = vhtfm.get_doc(doc)
	doc.save()

	return doc.as_dict()


@vhtfm.whitelist(methods=["POST", "PUT"])
def rename_doc(doctype, old_name, new_name, merge=False):
	"""Rename document

	:param doctype: DocType of the document to be renamed
	:param old_name: Current `name` of the document to be renamed
	:param new_name: New `name` to be set"""
	new_name = vhtfm.rename_doc(doctype, old_name, new_name, merge=merge)
	return new_name


@vhtfm.whitelist(methods=["POST", "PUT"])
def submit(doc):
	"""Submit a document

	:param doc: JSON or dict object to be submitted remotely"""
	if isinstance(doc, str):
		doc = json.loads(doc)

	doc = vhtfm.get_doc(doc)
	doc.submit()

	return doc.as_dict()


@vhtfm.whitelist(methods=["POST", "PUT"])
def cancel(doctype, name):
	"""Cancel a document

	:param doctype: DocType of the document to be cancelled
	:param name: name of the document to be cancelled"""
	wrapper = vhtfm.get_doc(doctype, name)
	wrapper.cancel()

	return wrapper.as_dict()


@vhtfm.whitelist(methods=["DELETE", "POST"])
def delete(doctype, name):
	"""Delete a remote document

	:param doctype: DocType of the document to be deleted
	:param name: name of the document to be deleted"""
	delete_doc(doctype, name)


@vhtfm.whitelist(methods=["POST", "PUT"])
def bulk_update(docs):
	"""Bulk update documents

	:param docs: JSON list of documents to be updated remotely. Each document must have `docname` property"""
	docs = json.loads(docs)
	failed_docs = []
	for doc in docs:
		doc.pop("flags", None)
		try:
			existing_doc = vhtfm.get_doc(doc["doctype"], doc["docname"])
			existing_doc.update(doc)
			existing_doc.save()
		except Exception:
			failed_docs.append({"doc": doc, "exc": vhtfm.utils.get_traceback()})

	return {"failed_docs": failed_docs}


@vhtfm.whitelist()
def has_permission(doctype, docname, perm_type="read"):
	"""Return a JSON with data whether the document has the requested permission.

	:param doctype: DocType of the document to be checked
	:param docname: `name` of the document to be checked
	:param perm_type: one of `read`, `write`, `create`, `submit`, `cancel`, `report`. Default is `read`"""
	# perm_type can be one of read, write, create, submit, cancel, report
	return {"has_permission": vhtfm.has_permission(doctype, perm_type.lower(), docname)}


@vhtfm.whitelist()
def get_doc_permissions(doctype, docname):
	"""Return an evaluated document permissions dict like `{"read":1, "write":1}`.

	:param doctype: DocType of the document to be evaluated
	:param docname: `name` of the document to be evaluated
	"""
	doc = vhtfm.get_doc(doctype, docname)
	return {"permissions": vhtfm.permissions.get_doc_permissions(doc)}


@vhtfm.whitelist()
def get_password(doctype, name, fieldname):
	"""Return a password type property. Only applicable for System Managers

	:param doctype: DocType of the document that holds the password
	:param name: `name` of the document that holds the password
	:param fieldname: `fieldname` of the password property
	"""
	vhtfm.only_for("System Manager")
	return vhtfm.get_doc(doctype, name).get_password(fieldname)


from vhtfm.deprecation_dumpster import get_js as _get_js

get_js = vhtfm.whitelist()(_get_js)


@vhtfm.whitelist(allow_guest=True)
def get_time_zone():
	"""Return the default time zone."""
	return {"time_zone": vhtfm.defaults.get_defaults().get("time_zone")}


@vhtfm.whitelist(methods=["POST", "PUT"])
def attach_file(
	filename=None,
	filedata=None,
	doctype=None,
	docname=None,
	folder=None,
	decode_base64=False,
	is_private=None,
	docfield=None,
):
	"""Attach a file to Document

	:param filename: filename e.g. test-file.txt
	:param filedata: base64 encode filedata which must be urlencoded
	:param doctype: Reference DocType to attach file to
	:param docname: Reference DocName to attach file to
	:param folder: Folder to add File into
	:param decode_base64: decode filedata from base64 encode, default is False
	:param is_private: Attach file as private file (1 or 0)
	:param docfield: file to attach to (optional)"""

	doc = vhtfm.get_doc(doctype, docname)
	doc.check_permission()

	file = vhtfm.get_doc(
		{
			"doctype": "File",
			"file_name": filename,
			"attached_to_doctype": doctype,
			"attached_to_name": docname,
			"attached_to_field": docfield,
			"folder": folder,
			"is_private": is_private,
			"content": filedata,
			"decode": decode_base64,
		}
	).save()

	if docfield and doctype:
		doc.set(docfield, file.file_url)
		doc.save()

	return file


@vhtfm.whitelist()
def is_document_amended(doctype, docname):
	if vhtfm.permissions.has_permission(doctype):
		try:
			return vhtfm.db.exists(doctype, {"amended_from": docname})
		except vhtfm.db.InternalError:
			pass

	return False


@vhtfm.whitelist()
def validate_link(doctype: str, docname: str, fields=None):
	if not isinstance(doctype, str):
		vhtfm.throw(_("DocType must be a string"))

	if not isinstance(docname, str):
		vhtfm.throw(_("Document Name must be a string"))

	if doctype != "DocType" and not (
		vhtfm.has_permission(doctype, "select") or vhtfm.has_permission(doctype, "read")
	):
		vhtfm.throw(
			_("You do not have Read or Select Permissions for {}").format(vhtfm.bold(doctype)),
			vhtfm.PermissionError,
		)

	values = vhtfm._dict()

	if is_virtual_doctype(doctype):
		try:
			vhtfm.get_doc(doctype, docname)
			values.name = docname
		except vhtfm.DoesNotExistError:
			vhtfm.clear_last_message()
			vhtfm.msgprint(
				_("Document {0} {1} does not exist").format(vhtfm.bold(doctype), vhtfm.bold(docname)),
			)
		return values

	values.name = vhtfm.db.get_value(doctype, docname, cache=True)

	fields = vhtfm.parse_json(fields)
	if not values.name or not fields:
		return values

	try:
		values.update(get_value(doctype, fields, docname))
	except vhtfm.PermissionError:
		vhtfm.clear_last_message()
		vhtfm.msgprint(
			_("You need {0} permission to fetch values from {1} {2}").format(
				vhtfm.bold(_("Read")), vhtfm.bold(doctype), vhtfm.bold(docname)
			),
			title=_("Cannot Fetch Values"),
			indicator="orange",
		)

	return values


def insert_doc(doc) -> "Document":
	"""Insert document and return parent document object with appended child document if `doc` is child document else return the inserted document object.

	:param doc: doc to insert (dict)"""

	doc = vhtfm._dict(doc)
	if vhtfm.is_table(doc.doctype):
		if not (doc.parenttype and doc.parent and doc.parentfield):
			vhtfm.throw(_("Parenttype, Parent and Parentfield are required to insert a child record"))

		# inserting a child record
		parent = vhtfm.get_doc(doc.parenttype, doc.parent)
		parent.append(doc.parentfield, doc)
		parent.save()
		return parent

	return vhtfm.get_doc(doc).insert()


def delete_doc(doctype, name):
	"""Deletes document
	if doctype is a child table, then deletes the child record using the parent doc
	so that the parent doc's `on_update` is called
	"""

	if vhtfm.is_table(doctype):
		values = vhtfm.db.get_value(doctype, name, ["parenttype", "parent", "parentfield"])
		if not values:
			raise vhtfm.DoesNotExistError
		parenttype, parent, parentfield = values
		parent = vhtfm.get_doc(parenttype, parent)
		for row in parent.get(parentfield):
			if row.name == name:
				parent.remove(row)
				parent.save()
				break
	else:
		vhtfm.delete_doc(doctype, name, ignore_missing=False)
