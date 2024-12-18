import vhtfm


# no context object is accepted
def get_context():
	context = vhtfm._dict()
	context.body = "Custom Content"
	return context
