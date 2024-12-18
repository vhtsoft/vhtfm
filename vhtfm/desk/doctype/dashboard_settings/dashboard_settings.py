# Copyright (c) 2020, Vhtfm Technologies and contributors
# License: MIT. See LICENSE

import json

import vhtfm

# import vhtfm
from vhtfm.model.document import Document


class DashboardSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from vhtfm.types import DF

		chart_config: DF.Code | None
		user: DF.Link | None
	# end: auto-generated types

	pass


@vhtfm.whitelist()
def create_dashboard_settings(user):
	if not vhtfm.db.exists("Dashboard Settings", user):
		doc = vhtfm.new_doc("Dashboard Settings")
		doc.name = user
		doc.insert(ignore_permissions=True)
		vhtfm.db.commit()
		return doc


def get_permission_query_conditions(user):
	if not user:
		user = vhtfm.session.user

	return f"""(`tabDashboard Settings`.name = {vhtfm.db.escape(user)})"""


@vhtfm.whitelist()
def save_chart_config(reset, config, chart_name):
	reset = vhtfm.parse_json(reset)
	doc = vhtfm.get_doc("Dashboard Settings", vhtfm.session.user)
	chart_config = vhtfm.parse_json(doc.chart_config) or {}

	if reset:
		chart_config[chart_name] = {}
	else:
		config = vhtfm.parse_json(config)
		if chart_name not in chart_config:
			chart_config[chart_name] = {}
		chart_config[chart_name].update(config)

	vhtfm.db.set_value("Dashboard Settings", vhtfm.session.user, "chart_config", json.dumps(chart_config))
