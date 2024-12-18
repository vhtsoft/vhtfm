import json

import vhtfm


def execute():
	"""Handle introduction of UI tours"""
	completed = {}
	for tour in vhtfm.get_all("Form Tour", {"ui_tour": 1}, pluck="name"):
		completed[tour] = {"is_complete": True}

	User = vhtfm.qb.DocType("User")
	vhtfm.qb.update(User).set("onboarding_status", json.dumps(completed)).run()
