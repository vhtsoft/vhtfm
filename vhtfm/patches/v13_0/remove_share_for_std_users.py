import vhtfm
import vhtfm.share


def execute():
	for user in vhtfm.STANDARD_USERS:
		vhtfm.share.remove("User", user, user)
