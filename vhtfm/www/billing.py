import vhtfm
from vhtfm.utils import cint

no_cache = 1


def get_context(context):
	vhtfm.db.commit()  # nosemgrep
	context = vhtfm._dict()
	context.boot = get_boot()
	return context


def get_boot():
	return vhtfm._dict(
		{
			"site_name": vhtfm.local.site,
			"read_only_mode": vhtfm.flags.read_only,
			"csrf_token": vhtfm.sessions.get_csrf_token(),
			"setup_complete": cint(vhtfm.get_system_settings("setup_complete")),
		}
	)
