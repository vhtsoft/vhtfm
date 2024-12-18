# Copyright (c) 2021, Vhtfm Technologies and contributors
# License: MIT. See LICENSE

import json

import vhtfm
from vhtfm import _
from vhtfm.model.document import Document
from vhtfm.modules.export_file import export_to_files


class FormTour(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from vhtfm.desk.doctype.form_tour_step.form_tour_step import FormTourStep
		from vhtfm.types import DF

		dashboard_name: DF.Link | None
		first_document: DF.Check
		include_name_field: DF.Check
		is_standard: DF.Check
		list_name: DF.Literal[
			"List", "Report", "Dashboard", "Kanban", "Gantt", "Calendar", "File", "Image", "Inbox", "Map"
		]
		module: DF.Link | None
		new_document_form: DF.Check
		page_name: DF.Link | None
		page_route: DF.SmallText | None
		reference_doctype: DF.Link | None
		report_name: DF.Link | None
		save_on_complete: DF.Check
		steps: DF.Table[FormTourStep]
		title: DF.Data
		track_steps: DF.Check
		ui_tour: DF.Check
		view_name: DF.Literal["Workspaces", "List", "Form", "Tree", "Page"]
		workspace_name: DF.Link | None
	# end: auto-generated types

	def before_save(self):
		if self.is_standard and not self.module:
			if self.workspace_name:
				self.module = vhtfm.db.get_value("Workspace", self.workspace_name, "module")
			elif self.dashboard_name:
				dashboard_doctype = vhtfm.db.get_value("Dashboard", self.dashboard_name, "module")
				self.module = vhtfm.db.get_value("DocType", dashboard_doctype, "module")
			else:
				self.module = "Desk"
		if not self.ui_tour:
			meta = vhtfm.get_meta(self.reference_doctype)
			for step in self.steps:
				if step.is_table_field and step.parent_fieldname:
					parent_field_df = meta.get_field(step.parent_fieldname)
					step.child_doctype = parent_field_df.options
					field_df = vhtfm.get_meta(step.child_doctype).get_field(step.fieldname)
					step.label = field_df.label
					step.fieldtype = field_df.fieldtype
				else:
					field_df = meta.get_field(step.fieldname)
					step.label = field_df.label
					step.fieldtype = field_df.fieldtype

	def on_update(self):
		vhtfm.cache.delete_key("bootinfo")

		if vhtfm.conf.developer_mode and self.is_standard:
			export_to_files([["Form Tour", self.name]], self.module)

	def on_trash(self):
		vhtfm.cache.delete_key("bootinfo")


@vhtfm.whitelist()
def reset_tour(tour_name):
	for user in vhtfm.get_all("User", pluck="name"):
		onboarding_status = vhtfm.parse_json(vhtfm.db.get_value("User", user, "onboarding_status"))
		onboarding_status.pop(tour_name, None)
		vhtfm.db.set_value(
			"User", user, "onboarding_status", vhtfm.as_json(onboarding_status), update_modified=False
		)
		vhtfm.cache.hdel("bootinfo", user)

	vhtfm.msgprint(_("Successfully reset onboarding status for all users."), alert=True)


@vhtfm.whitelist()
def update_user_status(value, step):
	from vhtfm.utils.telemetry import capture

	step = vhtfm.parse_json(step)
	tour = vhtfm.parse_json(value)

	capture(
		vhtfm.scrub(f"{step.parent}_{step.title}"),
		app="vhtfm_ui_tours",
		properties={"is_completed": tour.is_completed},
	)
	vhtfm.db.set_value("User", vhtfm.session.user, "onboarding_status", value, update_modified=False)

	vhtfm.cache.hdel("bootinfo", vhtfm.session.user)


def get_onboarding_ui_tours():
	if not vhtfm.get_system_settings("enable_onboarding"):
		return []

	ui_tours = vhtfm.get_all("Form Tour", filters={"ui_tour": 1}, fields=["page_route", "name"])

	return [[tour.name, json.loads(tour.page_route)] for tour in ui_tours]
