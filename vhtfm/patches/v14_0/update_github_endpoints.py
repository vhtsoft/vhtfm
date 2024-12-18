import json

import vhtfm


def execute():
	if vhtfm.db.exists("Social Login Key", "github"):
		vhtfm.db.set_value(
			"Social Login Key", "github", "auth_url_data", json.dumps({"scope": "user:email"})
		)
