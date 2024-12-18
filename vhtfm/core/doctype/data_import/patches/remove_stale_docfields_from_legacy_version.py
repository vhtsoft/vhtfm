import vhtfm


def execute():
	"""Remove stale docfields from legacy version"""
	vhtfm.db.delete("DocField", {"options": "Data Import", "parent": "Data Import Legacy"})
