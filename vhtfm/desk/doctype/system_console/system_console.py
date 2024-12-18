# Copyright (c) 2020, Vhtfm Technologies and contributors
# License: MIT. See LICENSE

import json

import vhtfm
from vhtfm.model.document import Document
from vhtfm.utils.safe_exec import read_sql, safe_exec


class SystemConsole(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from vhtfm.types import DF

		commit: DF.Check
		console: DF.Code | None
		output: DF.Code | None
		show_processlist: DF.Check
		type: DF.Literal["Python", "SQL"]
	# end: auto-generated types

	def run(self):
		vhtfm.only_for("System Manager")
		try:
			vhtfm.local.debug_log = []
			if self.type == "Python":
				safe_exec(self.console, script_filename="System Console")
				self.output = "\n".join(vhtfm.debug_log)
			elif self.type == "SQL":
				self.output = vhtfm.as_json(read_sql(self.console, as_dict=1))
		except Exception:
			self.commit = False
			self.output = vhtfm.get_traceback()

		if self.commit:
			vhtfm.db.commit()
		else:
			vhtfm.db.rollback()
		vhtfm.get_doc(
			doctype="Console Log", script=self.console, type=self.type, committed=self.commit
		).insert()
		vhtfm.db.commit()


@vhtfm.whitelist()
def execute_code(doc):
	console = vhtfm.get_doc(json.loads(doc))
	console.run()
	return console.as_dict()


@vhtfm.whitelist()
def show_processlist():
	vhtfm.only_for("System Manager")
	return _show_processlist()


def _show_processlist():
	return vhtfm.db.multisql(
		{
			"postgres": """
			SELECT pid AS "Id",
				query_start AS "Time",
				state AS "State",
				query AS "Info",
				wait_event AS "Progress"
			FROM pg_stat_activity""",
			"mariadb": "show full processlist",
		},
		as_dict=True,
	)
