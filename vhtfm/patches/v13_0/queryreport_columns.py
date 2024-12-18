# Copyright (c) 2021, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import json

import vhtfm


def execute():
	"""Convert Query Report json to support other content."""
	records = vhtfm.get_all("Report", filters={"json": ["!=", ""]}, fields=["name", "json"])
	for record in records:
		jstr = record["json"]
		data = json.loads(jstr)
		if isinstance(data, list):
			# double escape braces
			jstr = f'{{"columns":{jstr}}}'
			vhtfm.db.set_value("Report", record["name"], "json", jstr)
