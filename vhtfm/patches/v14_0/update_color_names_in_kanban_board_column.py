# Copyright (c) 2021, Vhtfm Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt


import vhtfm


def execute():
	indicator_map = {
		"blue": "Blue",
		"orange": "Orange",
		"red": "Red",
		"green": "Green",
		"darkgrey": "Gray",
		"gray": "Gray",
		"purple": "Purple",
		"yellow": "Yellow",
		"lightblue": "Light Blue",
	}
	for d in vhtfm.get_all("Kanban Board Column", fields=["name", "indicator"]):
		color_name = indicator_map.get(d.indicator, "Gray")
		vhtfm.db.set_value("Kanban Board Column", d.name, "indicator", color_name)
