import vhtfm


def execute():
	vhtfm.reload_doc("core", "doctype", "domain")
	vhtfm.reload_doc("core", "doctype", "has_domain")
	active_domains = vhtfm.get_active_domains()
	all_domains = vhtfm.get_all("Domain")

	for d in all_domains:
		if d.name not in active_domains:
			inactive_domain = vhtfm.get_doc("Domain", d.name)
			inactive_domain.setup_data()
			inactive_domain.remove_custom_field()
