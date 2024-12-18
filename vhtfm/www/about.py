# Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import vhtfm

sitemap = 1


def get_context(context):
	context.doc = vhtfm.get_cached_doc("About Us Settings")

	return context
