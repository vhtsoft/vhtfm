# Copyright (c) 2017, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import vhtfm


@vhtfm.whitelist()
def get_leaderboard_config():
	leaderboard_config = vhtfm._dict()
	leaderboard_hooks = vhtfm.get_hooks("leaderboards")
	for hook in leaderboard_hooks:
		leaderboard_config.update(vhtfm.get_attr(hook)())

	return leaderboard_config
