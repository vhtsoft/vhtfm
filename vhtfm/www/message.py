# Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import vhtfm
from vhtfm.utils import strip_html_tags
from vhtfm.utils.html_utils import clean_html

no_cache = 1


def get_context(context):
	message_context = vhtfm._dict()
	if hasattr(vhtfm.local, "message"):
		message_context["header"] = vhtfm.local.message_title
		message_context["title"] = strip_html_tags(vhtfm.local.message_title)
		message_context["message"] = vhtfm.local.message
		if hasattr(vhtfm.local, "message_success"):
			message_context["success"] = vhtfm.local.message_success

	elif vhtfm.local.form_dict.id:
		message_id = vhtfm.local.form_dict.id
		key = f"message_id:{message_id}"
		message = vhtfm.cache.get_value(key, expires=True)
		if message:
			message_context.update(message.get("context", {}))
			if message.get("http_status_code"):
				vhtfm.local.response["http_status_code"] = message["http_status_code"]

	if not message_context.title:
		message_context.title = clean_html(vhtfm.form_dict.title)

	if not message_context.message:
		message_context.message = clean_html(vhtfm.form_dict.message)

	return message_context
