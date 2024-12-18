import vhtfm


def execute():
	vhtfm.delete_doc_if_exists("DocType", "Post")
	vhtfm.delete_doc_if_exists("DocType", "Post Comment")
