# Copyright (c) 2019, Vhtfm Technologies and Contributors
# License: MIT. See LICENSE
import vhtfm
import vhtfm.cache_manager
from vhtfm.tests import IntegrationTestCase, UnitTestCase


class UnitTestMilestoneTracker(UnitTestCase):
	"""
	Unit tests for MilestoneTracker.
	Use this class for testing individual functions and methods.
	"""

	pass


class TestMilestoneTracker(IntegrationTestCase):
	def test_milestone(self):
		vhtfm.db.delete("Milestone Tracker")

		vhtfm.cache.delete_key("milestone_tracker_map")

		milestone_tracker = vhtfm.get_doc(
			doctype="Milestone Tracker", document_type="ToDo", track_field="status"
		).insert()

		todo = vhtfm.get_doc(doctype="ToDo", description="test milestone", status="Open").insert()

		milestones = vhtfm.get_all(
			"Milestone",
			fields=["track_field", "value", "milestone_tracker"],
			filters=dict(reference_type=todo.doctype, reference_name=todo.name),
		)

		self.assertEqual(len(milestones), 1)
		self.assertEqual(milestones[0].track_field, "status")
		self.assertEqual(milestones[0].value, "Open")

		todo.status = "Closed"
		todo.save()

		milestones = vhtfm.get_all(
			"Milestone",
			fields=["track_field", "value", "milestone_tracker"],
			filters=dict(reference_type=todo.doctype, reference_name=todo.name),
			order_by="creation desc",
		)

		self.assertEqual(len(milestones), 2)
		self.assertEqual(milestones[0].track_field, "status")
		self.assertEqual(milestones[0].value, "Closed")

		# cleanup
		vhtfm.db.delete("Milestone")
		milestone_tracker.delete()
