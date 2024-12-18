# Copyright (c) 2021, Vhtfm Technologies and contributors
# License: MIT. See LICENSE
from tenacity import retry, retry_if_exception_type, stop_after_attempt

import vhtfm
from vhtfm.model.document import Document
from vhtfm.utils import cstr


class AccessLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from vhtfm.types import DF

		columns: DF.HTMLEditor | None
		export_from: DF.Data | None
		file_type: DF.Data | None
		filters: DF.Code | None
		method: DF.Data | None
		page: DF.HTMLEditor | None
		reference_document: DF.Data | None
		report_name: DF.Data | None
		timestamp: DF.Datetime | None
		user: DF.Link | None
	# end: auto-generated types

	@staticmethod
	def clear_old_logs(days=30):
		from vhtfm.query_builder import Interval
		from vhtfm.query_builder.functions import Now

		table = vhtfm.qb.DocType("Access Log")
		vhtfm.db.delete(table, filters=(table.creation < (Now() - Interval(days=days))))


@vhtfm.whitelist()
def make_access_log(
	doctype=None,
	document=None,
	method=None,
	file_type=None,
	report_name=None,
	filters=None,
	page=None,
	columns=None,
):
	_make_access_log(
		doctype,
		document,
		method,
		file_type,
		report_name,
		filters,
		page,
		columns,
	)


@vhtfm.write_only()
@retry(
	stop=stop_after_attempt(3),
	retry=retry_if_exception_type(vhtfm.DuplicateEntryError),
	reraise=True,
)
def _make_access_log(
	doctype=None,
	document=None,
	method=None,
	file_type=None,
	report_name=None,
	filters=None,
	page=None,
	columns=None,
):
	user = vhtfm.session.user
	in_request = vhtfm.request and vhtfm.request.method == "GET"

	access_log = vhtfm.get_doc(
		{
			"doctype": "Access Log",
			"user": user,
			"export_from": doctype,
			"reference_document": document,
			"file_type": file_type,
			"report_name": report_name,
			"page": page,
			"method": method,
			"filters": cstr(filters) or None,
			"columns": columns,
		}
	)

	if vhtfm.flags.read_only:
		access_log.deferred_insert()
		return
	else:
		access_log.db_insert()

	# `vhtfm.db.commit` added because insert doesnt `commit` when called in GET requests like `printview`
	# dont commit in test mode. It must be tempting to put this block along with the in_request in the
	# whitelisted method...yeah, don't do it. That part would be executed possibly on a read only DB conn
	if not vhtfm.flags.in_test or in_request:
		vhtfm.db.commit()
