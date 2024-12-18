"""
Run this after updating country_info.json and or
"""

import vhtfm


def execute():
	for col in ("field", "doctype"):
		vhtfm.db.sql_ddl(f"alter table `tabSingles` modify column `{col}` varchar(255)")
