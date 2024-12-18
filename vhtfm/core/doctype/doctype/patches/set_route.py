import vhtfm
from vhtfm.desk.utils import slug


def execute():
	for doctype in vhtfm.get_all("DocType", ["name", "route"], dict(istable=0)):
		if not doctype.route:
			vhtfm.db.set_value("DocType", doctype.name, "route", slug(doctype.name), update_modified=False)
