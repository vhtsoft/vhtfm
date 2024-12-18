import click

import vhtfm


def execute():
	vhtfm.delete_doc_if_exists("DocType", "Chat Message")
	vhtfm.delete_doc_if_exists("DocType", "Chat Message Attachment")
	vhtfm.delete_doc_if_exists("DocType", "Chat Profile")
	vhtfm.delete_doc_if_exists("DocType", "Chat Token")
	vhtfm.delete_doc_if_exists("DocType", "Chat Room User")
	vhtfm.delete_doc_if_exists("DocType", "Chat Room")
	vhtfm.delete_doc_if_exists("Module Def", "Chat")

	click.secho(
		"Chat Module is moved to a separate app and is removed from Vhtfm in version-13.\n"
		"Please install the app to continue using the chat feature: https://github.com/vhtfm/chat",
		fg="yellow",
	)
