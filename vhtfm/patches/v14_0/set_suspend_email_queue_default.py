import vhtfm
from vhtfm.cache_manager import clear_defaults_cache


def execute():
	vhtfm.db.set_default(
		"suspend_email_queue",
		vhtfm.db.get_default("hold_queue", "Administrator") or 0,
		parent="__default",
	)

	vhtfm.db.delete("DefaultValue", {"defkey": "hold_queue"})
	clear_defaults_cache()
