import vhtfm


def execute():
	vhtfm.reload_doc("website", "doctype", "web_page_view", force=True)
	vhtfm.db.sql("""UPDATE `tabWeb Page View` set path='/' where path=''""")
