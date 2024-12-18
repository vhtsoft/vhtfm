# Copyright (c) 2022, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import vhtfm
from vhtfm.model import is_default_field
from vhtfm.query_builder import Order
from vhtfm.query_builder.functions import Count
from vhtfm.query_builder.terms import SubQuery
from vhtfm.query_builder.utils import DocType


@vhtfm.whitelist()
def get_list_settings(doctype):
	try:
		return vhtfm.get_cached_doc("List View Settings", doctype)
	except vhtfm.DoesNotExistError:
		vhtfm.clear_messages()


@vhtfm.whitelist()
def set_list_settings(doctype, values):
	try:
		doc = vhtfm.get_doc("List View Settings", doctype)
	except vhtfm.DoesNotExistError:
		doc = vhtfm.new_doc("List View Settings")
		doc.name = doctype
		vhtfm.clear_messages()
	doc.update(vhtfm.parse_json(values))
	doc.save()


@vhtfm.whitelist()
def get_group_by_count(doctype: str, current_filters: str, field: str) -> list[dict]:
	current_filters = vhtfm.parse_json(current_filters)

	if field == "assigned_to":
		ToDo = DocType("ToDo")
		User = DocType("User")
		count = Count("*").as_("count")
		filtered_records = vhtfm.qb.get_query(
			doctype,
			filters=current_filters,
			fields=["name"],
			validate_filters=True,
		)

		return (
			vhtfm.qb.from_(ToDo)
			.from_(User)
			.select(ToDo.allocated_to.as_("name"), count)
			.where(
				(ToDo.status != "Cancelled")
				& (ToDo.allocated_to == User.name)
				& (User.user_type == "System User")
				& (ToDo.reference_name.isin(SubQuery(filtered_records)))
			)
			.groupby(ToDo.allocated_to)
			.orderby(count, order=Order.desc)
			.limit(50)
			.run(as_dict=True)
		)

	meta = vhtfm.get_meta(doctype)

	if not meta.has_field(field) and not is_default_field(field):
		raise ValueError("Field does not belong to doctype")

	data = vhtfm.get_list(
		doctype,
		filters=current_filters,
		group_by=f"`tab{doctype}`.{field}",
		fields=["count(*) as count", f"`{field}` as name"],
		order_by="count desc",
		limit=1000,
	)

	if field == "owner":
		owner_idx = None

		for idx, item in enumerate(data):
			if item.name == vhtfm.session.user:
				owner_idx = idx
				break

		if owner_idx:
			data = [data.pop(owner_idx)] + data[0:49]
		else:
			data = data[0:50]
	else:
		data = data[0:50]

	# Add in title if it's a link field and `show_title_field_in_link` is set
	if (field_meta := meta.get_field(field)) and field_meta.fieldtype == "Link":
		link_meta = vhtfm.get_meta(field_meta.options)
		if link_meta.show_title_field_in_link:
			title_field = link_meta.get_title_field()
			for item in data:
				item.title = vhtfm.get_value(field_meta.options, item.name, title_field)

	return data
