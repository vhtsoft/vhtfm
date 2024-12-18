# Copyright (c) 2019, Vhtfm Technologies and contributors
# License: MIT. See LICENSE

import vhtfm
import vhtfm.cache_manager
from vhtfm.model import log_types
from vhtfm.model.document import Document


class MilestoneTracker(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from vhtfm.types import DF

		disabled: DF.Check
		document_type: DF.Link
		track_field: DF.Literal[None]
	# end: auto-generated types

	def on_update(self):
		vhtfm.cache_manager.clear_doctype_map("Milestone Tracker", self.document_type)

	def on_trash(self):
		vhtfm.cache_manager.clear_doctype_map("Milestone Tracker", self.document_type)

	def apply(self, doc):
		before_save = doc.get_doc_before_save()
		from_value = (before_save and before_save.get(self.track_field)) or None
		if from_value != doc.get(self.track_field):
			vhtfm.get_doc(
				doctype="Milestone",
				reference_type=doc.doctype,
				reference_name=doc.name,
				track_field=self.track_field,
				from_value=from_value,
				value=doc.get(self.track_field),
				milestone_tracker=self.name,
			).insert(ignore_permissions=True)


def evaluate_milestone(doc, event):
	if (
		vhtfm.flags.in_install
		or vhtfm.flags.in_migrate
		or vhtfm.flags.in_setup_wizard
		or doc.doctype in log_types
	):
		return

	# track milestones related to this doctype
	for d in get_milestone_trackers(doc.doctype):
		vhtfm.get_doc("Milestone Tracker", d.get("name")).apply(doc)


def get_milestone_trackers(doctype):
	return vhtfm.cache_manager.get_doctype_map(
		"Milestone Tracker", doctype, dict(document_type=doctype, disabled=0)
	)
