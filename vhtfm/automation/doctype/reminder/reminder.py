# Copyright (c) 2023, Vhtfm Technologies and contributors
# For license information, please see license.txt

import vhtfm
from vhtfm import _
from vhtfm.model.document import Document
from vhtfm.utils import cint
from vhtfm.utils.data import add_to_date, get_datetime, now_datetime


class Reminder(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from vhtfm.types import DF

		description: DF.SmallText
		notified: DF.Check
		remind_at: DF.Datetime
		reminder_docname: DF.DynamicLink | None
		reminder_doctype: DF.Link | None
		user: DF.Link
	# end: auto-generated types

	@staticmethod
	def clear_old_logs(days=30):
		from vhtfm.query_builder import Interval
		from vhtfm.query_builder.functions import Now

		table = vhtfm.qb.DocType("Reminder")
		vhtfm.db.delete(table, filters=(table.remind_at < (Now() - Interval(days=days))))

	def validate(self):
		self.user = vhtfm.session.user
		if get_datetime(self.remind_at) < now_datetime():
			vhtfm.throw(_("Reminder cannot be created in past."))

	def send_reminder(self):
		if self.notified:
			return

		self.db_set("notified", 1, update_modified=False)

		try:
			notification = vhtfm.new_doc("Notification Log")
			notification.for_user = self.user
			notification.set("type", "Alert")
			notification.document_type = self.reminder_doctype
			notification.document_name = self.reminder_docname
			notification.subject = self.description
			notification.insert()
		except Exception:
			self.log_error("Failed to send reminder")


@vhtfm.whitelist()
def create_new_reminder(
	remind_at: str,
	description: str,
	reminder_doctype: str | None = None,
	reminder_docname: str | None = None,
):
	reminder = vhtfm.new_doc("Reminder")

	reminder.description = description
	reminder.remind_at = remind_at
	reminder.reminder_doctype = reminder_doctype
	reminder.reminder_docname = reminder_docname

	return reminder.insert()


def send_reminders():
	# Ensure that we send all reminders that might be before next job execution.
	job_freq = cint(vhtfm.get_conf().scheduler_interval) or 240
	upper_threshold = add_to_date(now_datetime(), seconds=job_freq, as_string=True, as_datetime=True)

	lower_threshold = add_to_date(now_datetime(), hours=-8, as_string=True, as_datetime=True)

	pending_reminders = vhtfm.get_all(
		"Reminder",
		filters=[
			("remind_at", "<=", upper_threshold),
			("remind_at", ">=", lower_threshold),  # dont send too old reminders if failed to send
			("notified", "=", 0),
		],
		pluck="name",
	)

	for reminder in pending_reminders:
		vhtfm.get_doc("Reminder", reminder).send_reminder()
