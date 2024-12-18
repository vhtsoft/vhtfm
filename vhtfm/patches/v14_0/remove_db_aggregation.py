import re

import vhtfm
from vhtfm.query_builder import DocType


def execute():
	"""Replace temporarily available Database Aggregate APIs on vhtfm (develop)

	APIs changed:
	        * vhtfm.db.max => vhtfm.qb.max
	        * vhtfm.db.min => vhtfm.qb.min
	        * vhtfm.db.sum => vhtfm.qb.sum
	        * vhtfm.db.avg => vhtfm.qb.avg
	"""
	ServerScript = DocType("Server Script")
	server_scripts = (
		vhtfm.qb.from_(ServerScript)
		.where(
			ServerScript.script.like("%vhtfm.db.max(%")
			| ServerScript.script.like("%vhtfm.db.min(%")
			| ServerScript.script.like("%vhtfm.db.sum(%")
			| ServerScript.script.like("%vhtfm.db.avg(%")
		)
		.select("name", "script")
		.run(as_dict=True)
	)

	for server_script in server_scripts:
		name, script = server_script["name"], server_script["script"]

		for agg in ["avg", "max", "min", "sum"]:
			script = re.sub(f"vhtfm.db.{agg}\\(", f"vhtfm.qb.{agg}(", script)

		vhtfm.db.set_value("Server Script", name, "script", script)
