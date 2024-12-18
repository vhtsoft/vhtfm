# Copyright (c) 2021, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

from click import secho

import vhtfm


def execute():
	if vhtfm.get_hooks("jenv"):
		print()
		secho(
			'WARNING: The hook "jenv" is deprecated. Follow the migration guide to use the new "jinja" hook.',
			fg="yellow",
		)
		secho("https://github.com/vhtfm/vhtfm/wiki/Migrating-to-Version-13", fg="yellow")
		print()
