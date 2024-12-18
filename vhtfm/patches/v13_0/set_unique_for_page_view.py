import vhtfm


def execute():
	vhtfm.reload_doc("website", "doctype", "web_page_view", force=True)
	site_url = vhtfm.utils.get_site_url(vhtfm.local.site)
	vhtfm.db.sql(f"""UPDATE `tabWeb Page View` set is_unique=1 where referrer LIKE '%{site_url}%'""")
