# Copyright (c) 2018, Vhtfm Technologies and contributors
# License: MIT. See LICENSE

import json

import vhtfm
from vhtfm import _
from vhtfm.desk.doctype.notification_log.notification_log import (
	enqueue_create_notification,
	get_title,
	get_title_html,
)
from vhtfm.desk.doctype.notification_settings.notification_settings import (
	is_email_notifications_enabled,
	is_email_notifications_enabled_for_type,
)
from vhtfm.model.document import Document
from vhtfm.utils import cint, get_fullname, get_link_to_form, getdate


class EnergyPointLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from vhtfm.types import DF

		points: DF.Int
		reason: DF.Text | None
		reference_doctype: DF.Link | None
		reference_name: DF.Data | None
		revert_of: DF.Link | None
		reverted: DF.Check
		rule: DF.Link | None
		seen: DF.Check
		type: DF.Literal["Auto", "Appreciation", "Criticism", "Review", "Revert"]
		user: DF.Link
	# end: auto-generated types

	def validate(self):
		self.map_milestone_reference()
		if self.type in ["Appreciation", "Criticism"] and self.user == self.owner:
			vhtfm.throw(_("You cannot give review points to yourself"))

	def map_milestone_reference(self):
		# link energy point to the original reference, if set by milestone
		if self.reference_doctype == "Milestone":
			self.reference_doctype, self.reference_name = vhtfm.db.get_value(
				"Milestone", self.reference_name, ["reference_type", "reference_name"]
			)

	def after_insert(self):
		alert_dict = get_alert_dict(self)
		if alert_dict:
			vhtfm.publish_realtime(
				"energy_point_alert", message=alert_dict, user=self.user, after_commit=True
			)

		vhtfm.cache.hdel("energy_points", self.user)

		if self.type != "Review" and vhtfm.get_cached_value(
			"Notification Settings", self.user, "energy_points_system_notifications"
		):
			reference_user = self.user if self.type == "Auto" else self.owner
			notification_doc = {
				"type": "Energy Point",
				"document_type": self.reference_doctype,
				"document_name": self.reference_name,
				"subject": get_notification_message(self),
				"from_user": reference_user,
				"email_content": f"<div>{self.reason}</div>" if self.reason else None,
			}

			enqueue_create_notification(self.user, notification_doc)

	def on_trash(self):
		if self.type == "Revert":
			reference_log = vhtfm.get_doc("Energy Point Log", self.revert_of)
			reference_log.reverted = 0
			reference_log.save()

	@vhtfm.whitelist()
	def revert(self, reason, ignore_permissions=False):
		if not ignore_permissions:
			vhtfm.only_for("System Manager")

		if self.type != "Auto":
			vhtfm.throw(_("This document cannot be reverted"))

		if self.get("reverted"):
			return

		self.reverted = 1
		self.save(ignore_permissions=True)

		return vhtfm.get_doc(
			{
				"doctype": "Energy Point Log",
				"points": -(self.points),
				"type": "Revert",
				"user": self.user,
				"reason": reason,
				"reference_doctype": self.reference_doctype,
				"reference_name": self.reference_name,
				"revert_of": self.name,
			}
		).insert(ignore_permissions=True)


def get_notification_message(doc):
	owner_name = get_fullname(doc.owner)
	points = doc.points
	title = get_title(doc.reference_doctype, doc.reference_name)

	if doc.type == "Auto":
		owner_name = vhtfm.bold("You")
		if points == 1:
			message = _("{0} gained {1} point for {2} {3}")
		else:
			message = _("{0} gained {1} points for {2} {3}")
		message = message.format(owner_name, vhtfm.bold(points), doc.rule, get_title_html(title))
	elif doc.type == "Appreciation":
		if points == 1:
			message = _("{0} appreciated your work on {1} with {2} point")
		else:
			message = _("{0} appreciated your work on {1} with {2} points")
		message = message.format(vhtfm.bold(owner_name), get_title_html(title), vhtfm.bold(points))
	elif doc.type == "Criticism":
		if points == 1:
			message = _("{0} criticized your work on {1} with {2} point")
		else:
			message = _("{0} criticized your work on {1} with {2} points")

		message = message.format(vhtfm.bold(owner_name), get_title_html(title), vhtfm.bold(points))
	elif doc.type == "Revert":
		if points == 1:
			message = _("{0} reverted your point on {1}")
		else:
			message = _("{0} reverted your points on {1}")
		message = message.format(vhtfm.bold(owner_name), get_title_html(title))

	return message


def get_alert_dict(doc):
	alert_dict = vhtfm._dict()
	owner_name = get_fullname(doc.owner)
	if doc.reference_doctype:
		doc_link = get_link_to_form(doc.reference_doctype, doc.reference_name)
	points = doc.points
	bold_points = vhtfm.bold(doc.points)
	if doc.type == "Auto":
		if points == 1:
			message = _("You gained {0} point")
		else:
			message = _("You gained {0} points")
		alert_dict.message = message.format(bold_points)
		alert_dict.indicator = "green"
	elif doc.type == "Appreciation":
		if points == 1:
			message = _("{0} appreciated your work on {1} with {2} point")
		else:
			message = _("{0} appreciated your work on {1} with {2} points")
		alert_dict.message = message.format(owner_name, doc_link, bold_points)
		alert_dict.indicator = "green"
	elif doc.type == "Criticism":
		if points == 1:
			message = _("{0} criticized your work on {1} with {2} point")
		else:
			message = _("{0} criticized your work on {1} with {2} points")

		alert_dict.message = message.format(owner_name, doc_link, bold_points)
		alert_dict.indicator = "red"
	elif doc.type == "Revert":
		if points == 1:
			message = _("{0} reverted your point on {1}")
		else:
			message = _("{0} reverted your points on {1}")
		alert_dict.message = message.format(
			owner_name,
			doc_link,
		)
		alert_dict.indicator = "red"

	return alert_dict


def create_energy_points_log(ref_doctype, ref_name, doc, apply_only_once=False):
	doc = vhtfm._dict(doc)
	if doc.rule:
		log_exists = check_if_log_exists(
			ref_doctype, ref_name, doc.rule, None if apply_only_once else doc.user
		)
		if log_exists:
			return vhtfm.get_doc("Energy Point Log", log_exists)

	new_log = vhtfm.new_doc("Energy Point Log")
	new_log.reference_doctype = ref_doctype
	new_log.reference_name = ref_name
	new_log.update(doc)
	new_log.insert(ignore_permissions=True)
	return new_log


def check_if_log_exists(ref_doctype, ref_name, rule, user=None):
	"""'Checks if Energy Point Log already exists"""
	filters = vhtfm._dict(
		{"rule": rule, "reference_doctype": ref_doctype, "reference_name": ref_name, "reverted": 0}
	)

	if user:
		filters.user = user

	return vhtfm.db.exists("Energy Point Log", filters)


def create_review_points_log(user, points, reason=None, doctype=None, docname=None):
	return vhtfm.get_doc(
		{
			"doctype": "Energy Point Log",
			"points": points,
			"type": "Review",
			"user": user,
			"reason": reason,
			"reference_doctype": doctype,
			"reference_name": docname,
		}
	).insert(ignore_permissions=True)


@vhtfm.whitelist()
def add_review_points(user, points):
	vhtfm.only_for("System Manager")
	create_review_points_log(user, points)


@vhtfm.whitelist()
def get_energy_points(user):
	points = get_user_energy_and_review_points(user)
	return vhtfm._dict(points.get(user, {}))


@vhtfm.whitelist()
def get_user_energy_and_review_points(user=None, from_date=None, as_dict=True):
	conditions = ""
	given_points_condition = ""
	values = vhtfm._dict()
	if user:
		conditions = "WHERE `user` = %(user)s"
		values.user = user
	if from_date:
		conditions += "WHERE" if not conditions else "AND"
		given_points_condition += "AND `creation` >= %(from_date)s"
		conditions += " `creation` >= %(from_date)s OR `type`='Review'"
		values.from_date = from_date

	points_list = vhtfm.db.sql(
		f"""
		SELECT
			SUM(CASE WHEN `type` != 'Review' THEN `points` ELSE 0 END) AS energy_points,
			SUM(CASE WHEN `type` = 'Review' THEN `points` ELSE 0 END) AS review_points,
			SUM(CASE
				WHEN `type`='Review' AND `points` < 0 {given_points_condition}
				THEN ABS(`points`)
				ELSE 0
			END) as given_points,
			`user`
		FROM `tabEnergy Point Log`
		{conditions}
		GROUP BY `user`
		ORDER BY `energy_points` DESC
	""",
		values=values,
		as_dict=1,
	)

	if not as_dict:
		return points_list

	dict_to_return = vhtfm._dict()
	for d in points_list:
		dict_to_return[d.pop("user")] = d
	return dict_to_return


@vhtfm.whitelist()
def review(doc, points, to_user, reason, review_type="Appreciation"):
	current_review_points = get_energy_points(vhtfm.session.user).review_points
	doc = doc.as_dict() if hasattr(doc, "as_dict") else vhtfm._dict(json.loads(doc))
	points = abs(cint(points))
	if current_review_points < points:
		vhtfm.msgprint(_("You do not have enough review points"))
		return

	review_doc = create_energy_points_log(
		doc.doctype,
		doc.name,
		{
			"type": review_type,
			"reason": reason,
			"points": points if review_type == "Appreciation" else -points,
			"user": to_user,
		},
	)

	# deduct review points from reviewer
	create_review_points_log(
		user=vhtfm.session.user,
		points=-points,
		reason=reason,
		doctype=review_doc.doctype,
		docname=review_doc.name,
	)

	return review_doc


@vhtfm.whitelist()
def get_reviews(doctype, docname):
	return vhtfm.get_all(
		"Energy Point Log",
		filters={
			"reference_doctype": doctype,
			"reference_name": docname,
			"type": ["in", ("Appreciation", "Criticism")],
		},
		fields=["points", "owner", "type", "user", "reason", "creation"],
	)


def send_weekly_summary():
	send_summary("Weekly")


def send_monthly_summary():
	send_summary("Monthly")


def send_summary(timespan):
	from vhtfm.social.doctype.energy_point_settings.energy_point_settings import (
		is_energy_point_enabled,
	)
	from vhtfm.utils.user import get_enabled_system_users

	if not is_energy_point_enabled():
		return

	if not is_email_notifications_enabled_for_type(vhtfm.session.user, "Energy Point"):
		return

	from_date = vhtfm.utils.add_to_date(None, weeks=-1)
	if timespan == "Monthly":
		from_date = vhtfm.utils.add_to_date(None, months=-1)

	user_points = get_user_energy_and_review_points(from_date=from_date, as_dict=False)

	# do not send report if no activity found
	if not user_points or not user_points[0].energy_points:
		return

	from_date = getdate(from_date)
	to_date = getdate()

	# select only those users that have energy point email notifications enabled
	all_users = [
		user.email
		for user in get_enabled_system_users()
		if is_email_notifications_enabled_for_type(user.name, "Energy Point")
	]

	vhtfm.sendmail(
		subject=f"{timespan} energy points summary",
		recipients=all_users,
		template="energy_points_summary",
		args={
			"top_performer": user_points[0],
			"top_reviewer": max(user_points, key=lambda x: x["given_points"]),
			"standings": user_points[:10],  # top 10
			"footer_message": get_footer_message(timespan).format(from_date, to_date),
		},
		with_container=1,
	)


def get_footer_message(timespan):
	if timespan == "Monthly":
		return _("Stats based on last month's performance (from {0} to {1})")
	else:
		return _("Stats based on last week's performance (from {0} to {1})")
