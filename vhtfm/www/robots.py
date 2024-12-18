import vhtfm

base_template_path = "www/robots.txt"


def get_context(context):
	robots_txt = (
		vhtfm.db.get_single_value("Website Settings", "robots_txt")
		or (vhtfm.local.conf.robots_txt and vhtfm.read_file(vhtfm.local.conf.robots_txt))
		or ""
	)

	return {"robots_txt": robots_txt}
