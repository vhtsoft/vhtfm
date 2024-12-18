# Copyright (c) 2022, Vhtfm Technologies and contributors
# License: MIT. See LICENSE

import vhtfm
from vhtfm.deferred_insert import deferred_insert as _deferred_insert
from vhtfm.model.document import Document


class RouteHistory(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from vhtfm.types import DF

		route: DF.Data | None
		user: DF.Link | None
	# end: auto-generated types

	@staticmethod
	def clear_old_logs(days=30):
		from vhtfm.query_builder import Interval
		from vhtfm.query_builder.functions import Now

		table = vhtfm.qb.DocType("Route History")
		vhtfm.db.delete(table, filters=(table.creation < (Now() - Interval(days=days))))


@vhtfm.whitelist()
def deferred_insert(routes):
	routes = [
		{
			"user": vhtfm.session.user,
			"route": route.get("route"),
			"creation": route.get("creation"),
		}
		for route in vhtfm.parse_json(routes)
	]

	_deferred_insert("Route History", routes)


@vhtfm.whitelist()
def frequently_visited_links():
	return vhtfm.get_all(
		"Route History",
		fields=["route", "count(name) as count"],
		filters={"user": vhtfm.session.user},
		group_by="route",
		order_by="count desc",
		limit=5,
	)
