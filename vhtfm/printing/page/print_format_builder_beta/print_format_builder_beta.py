# Copyright (c) 2021, Vhtfm Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt


import functools

import vhtfm


@vhtfm.whitelist()
def get_google_fonts():
	return _get_google_fonts()


@functools.lru_cache
def _get_google_fonts():
	file_path = vhtfm.get_app_path("vhtfm", "data", "google_fonts.json")
	return vhtfm.parse_json(vhtfm.read_file(file_path))
