import vhtfm


def execute():
	vhtfm.db.sql(
		"""
		UPDATE tabFile
		SET folder = 'Home/Attachments'
		WHERE ifnull(attached_to_doctype, '') != ''
		AND folder = 'Home'
	"""
	)
