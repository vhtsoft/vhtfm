from datetime import datetime

import vhtfm
from vhtfm.query_builder import Interval, Order
from vhtfm.query_builder.functions import Date, Sum, UnixTimestamp
from vhtfm.utils import getdate


@vhtfm.whitelist()
def get_energy_points_heatmap_data(user, date):
	try:
		date = getdate(date)
	except Exception:
		date = getdate()

	eps_log = vhtfm.qb.DocType("Energy Point Log")

	return dict(
		vhtfm.qb.from_(eps_log)
		.select(UnixTimestamp(Date(eps_log.creation)), Sum(eps_log.points))
		.where(eps_log.user == user)
		.where(eps_log["type"] != "Review")
		.where(Date(eps_log.creation) > Date(date) - Interval(years=1))
		.where(Date(eps_log.creation) < Date(date) + Interval(years=1))
		.groupby(Date(eps_log.creation))
		.orderby(Date(eps_log.creation), order=Order.asc)
		.run()
	)


@vhtfm.whitelist()
def get_energy_points_percentage_chart_data(user, field):
	result = vhtfm.get_all(
		"Energy Point Log",
		filters={"user": user, "type": ["!=", "Review"]},
		group_by=field,
		order_by=field,
		fields=[field, "ABS(sum(points)) as points"],
		as_list=True,
	)

	return {
		"labels": [r[0] for r in result if r[0] is not None],
		"datasets": [{"values": [r[1] for r in result]}],
	}


@vhtfm.whitelist()
def get_user_rank(user):
	month_start = datetime.today().replace(day=1)
	monthly_rank = vhtfm.get_all(
		"Energy Point Log",
		group_by="`tabEnergy Point Log`.`user`",
		filters={"creation": [">", month_start], "type": ["!=", "Review"]},
		fields=["user", "sum(points)"],
		order_by="sum(points) desc",
		as_list=True,
	)

	all_time_rank = vhtfm.get_all(
		"Energy Point Log",
		group_by="`tabEnergy Point Log`.`user`",
		filters={"type": ["!=", "Review"]},
		fields=["user", "sum(points)"],
		order_by="sum(points) desc",
		as_list=True,
	)

	return {
		"monthly_rank": [i + 1 for i, r in enumerate(monthly_rank) if r[0] == user],
		"all_time_rank": [i + 1 for i, r in enumerate(all_time_rank) if r[0] == user],
	}


@vhtfm.whitelist()
def update_profile_info(profile_info):
	profile_info = vhtfm.parse_json(profile_info)
	keys = ["location", "interest", "user_image", "bio"]

	for key in keys:
		if key not in profile_info:
			profile_info[key] = None

	user = vhtfm.get_doc("User", vhtfm.session.user)
	user.update(profile_info)
	user.save()
	return user


@vhtfm.whitelist()
def get_energy_points_list(start, limit, user):
	return vhtfm.db.get_list(
		"Energy Point Log",
		filters={"user": user, "type": ["!=", "Review"]},
		fields=[
			"name",
			"user",
			"points",
			"reference_doctype",
			"reference_name",
			"reason",
			"type",
			"seen",
			"rule",
			"owner",
			"creation",
			"revert_of",
		],
		start=start,
		limit=limit,
		order_by="creation desc",
	)
