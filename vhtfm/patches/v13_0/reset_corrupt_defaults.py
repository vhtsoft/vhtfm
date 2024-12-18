import vhtfm
from vhtfm.patches.v13_0.encrypt_2fa_secrets import DOCTYPE
from vhtfm.patches.v13_0.encrypt_2fa_secrets import PARENT_FOR_DEFAULTS as TWOFACTOR_PARENT
from vhtfm.utils import cint


def execute():
	"""
	This patch is needed to fix parent incorrectly set as `__2fa` because of
	https://github.com/vhtfm/vhtfm/commit/a822092211533ff17ff9b92dd86f6f868ed63e2e
	"""

	if not vhtfm.db.get_value(
		DOCTYPE, {"parent": TWOFACTOR_PARENT, "defkey": ("not like", "%_otp%")}, "defkey"
	):
		return

	# system settings
	system_settings = vhtfm.get_single("System Settings")
	system_settings.set_defaults()

	# home page
	vhtfm.db.set_default(
		"desktop:home_page", "workspace" if cint(system_settings.setup_complete) else "setup-wizard"
	)

	# letter head
	try:
		letter_head = vhtfm.get_doc("Letter Head", {"is_default": 1})
		letter_head.set_as_default()

	except vhtfm.DoesNotExistError:
		pass
