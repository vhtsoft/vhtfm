import vhtfm

VHTFM_CLOUD_DOMAINS = ("vhtfm.cloud", "vhterp.com", "vhtfmhr.com")


def on_vhtfmcloud() -> bool:
	"""Returns true if running on Vhtfm Cloud.


	Useful for modifying few features for better UX."""
	return vhtfm.local.site.endswith(VHTFM_CLOUD_DOMAINS)
