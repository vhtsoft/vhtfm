import vhtfm


def execute():
	vhtfm.reload_doc("core", "doctype", "user")
	vhtfm.db.sql(
		"""
		UPDATE `tabUser`
		SET `home_settings` = ''
		WHERE `user_type` = 'System User'
	"""
	)
