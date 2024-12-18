import vhtfm


def execute():
	"""
	Deprecate Feedback Trigger and Rating. This feature was not customizable.
	Now can be achieved via custom Web Forms
	"""
	vhtfm.delete_doc("DocType", "Feedback Trigger")
	vhtfm.delete_doc("DocType", "Feedback Rating")
