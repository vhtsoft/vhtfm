import vhtfm


def execute():
	vhtfm.delete_doc_if_exists("DocType", "Web View")
	vhtfm.delete_doc_if_exists("DocType", "Web View Component")
	vhtfm.delete_doc_if_exists("DocType", "CSS Class")
