# Copyright (c) 2022, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import contextlib
import functools
import json
import os
from textwrap import dedent

import vhtfm
import vhtfm.model.sync
import vhtfm.modules.patch_handler
import vhtfm.translate
from vhtfm.cache_manager import clear_global_cache
from vhtfm.core.doctype.language.language import sync_languages
from vhtfm.core.doctype.navbar_settings.navbar_settings import sync_standard_items
from vhtfm.core.doctype.scheduled_job_type.scheduled_job_type import sync_jobs
from vhtfm.database.schema import add_column
from vhtfm.deferred_insert import save_to_db as flush_deferred_inserts
from vhtfm.desk.notifications import clear_notifications
from vhtfm.modules.patch_handler import PatchType
from vhtfm.modules.utils import sync_customizations
from vhtfm.search.website_search import build_index_for_all_routes
from vhtfm.utils.connections import check_connection
from vhtfm.utils.dashboard import sync_dashboards
from vhtfm.utils.fixtures import sync_fixtures
from vhtfm.website.utils import clear_website_cache

FOX_START_MESSAGE = dedent(
	"""
	Cannot run fox migrate without the services running.
	If you are running fox in development mode, make sure that fox is running:

	$ fox start

	Otherwise, check the server logs and ensure that all the required services are running.
	"""
)


def atomic(method):
	@functools.wraps(method)
	def wrapper(*args, **kwargs):
		try:
			ret = method(*args, **kwargs)
			vhtfm.db.commit()
			return ret
		except Exception as e:
			# database itself can be gone while attempting rollback.
			# We should preserve original exception in this case.
			with contextlib.suppress(Exception):
				vhtfm.db.rollback()
			raise e

	return wrapper


class SiteMigration:
	"""Migrate all apps to the current version, will:
	- run before migrate hooks
	- run patches
	- sync doctypes (schema)
	- sync dashboards
	- sync jobs
	- sync fixtures
	- sync customizations
	- sync languages
	- sync web pages (from /www)
	- run after migrate hooks
	"""

	def __init__(self, skip_failing: bool = False, skip_search_index: bool = False) -> None:
		self.skip_failing = skip_failing
		self.skip_search_index = skip_search_index

	def setUp(self):
		"""Complete setup required for site migration"""
		vhtfm.flags.touched_tables = set()
		self.touched_tables_file = vhtfm.get_site_path("touched_tables.json")
		vhtfm.clear_cache()
		add_column(doctype="DocType", column_name="migration_hash", fieldtype="Data")
		clear_global_cache()

		if os.path.exists(self.touched_tables_file):
			os.remove(self.touched_tables_file)

		vhtfm.flags.in_migrate = True

	def tearDown(self):
		"""Run operations that should be run post schema updation processes
		This should be executed irrespective of outcome
		"""
		vhtfm.translate.clear_cache()
		clear_website_cache()
		clear_notifications()

		with open(self.touched_tables_file, "w") as f:
			json.dump(list(vhtfm.flags.touched_tables), f, sort_keys=True, indent=4)

		if not self.skip_search_index:
			print(f"Queued rebuilding of search index for {vhtfm.local.site}")
			vhtfm.enqueue(build_index_for_all_routes, queue="long")

		vhtfm.publish_realtime("version-update")
		vhtfm.flags.touched_tables.clear()
		vhtfm.flags.in_migrate = False

	@atomic
	def pre_schema_updates(self):
		"""Executes `before_migrate` hooks"""
		for app in vhtfm.get_installed_apps():
			for fn in vhtfm.get_hooks("before_migrate", app_name=app):
				vhtfm.get_attr(fn)()

	@atomic
	def run_schema_updates(self):
		"""Run patches as defined in patches.txt, sync schema changes as defined in the {doctype}.json files"""
		vhtfm.modules.patch_handler.run_all(
			skip_failing=self.skip_failing, patch_type=PatchType.pre_model_sync
		)
		vhtfm.model.sync.sync_all()
		vhtfm.modules.patch_handler.run_all(
			skip_failing=self.skip_failing, patch_type=PatchType.post_model_sync
		)

	@atomic
	def post_schema_updates(self):
		"""Execute pending migration tasks post patches execution & schema sync
		This includes:
		* Sync `Scheduled Job Type` and scheduler events defined in hooks
		* Sync fixtures & custom scripts
		* Sync in-Desk Module Dashboards
		* Sync customizations: Custom Fields, Property Setters, Custom Permissions
		* Sync Vhtfm's internal language master
		* Flush deferred inserts made during maintenance mode.
		* Sync Portal Menu Items
		* Sync Installed Applications Version History
		* Execute `after_migrate` hooks
		"""
		print("Syncing jobs...")
		sync_jobs()

		print("Syncing fixtures...")
		sync_fixtures()
		sync_standard_items()

		print("Syncing dashboards...")
		sync_dashboards()

		print("Syncing customizations...")
		sync_customizations()

		print("Syncing languages...")
		sync_languages()

		print("Flushing deferred inserts...")
		flush_deferred_inserts()

		print("Removing orphan doctypes...")
		vhtfm.model.sync.remove_orphan_doctypes()

		print("Syncing portal menu...")
		vhtfm.get_single("Portal Settings").sync_menu()

		print("Updating installed applications...")
		vhtfm.get_single("Installed Applications").update_versions()

		print("Executing `after_migrate` hooks...")
		for app in vhtfm.get_installed_apps():
			for fn in vhtfm.get_hooks("after_migrate", app_name=app):
				vhtfm.get_attr(fn)()

	def required_services_running(self) -> bool:
		"""Return True if all required services are running. Return False and print
		instructions to stdout when required services are not available.
		"""
		service_status = check_connection(redis_services=["redis_cache"])
		are_services_running = all(service_status.values())

		if not are_services_running:
			for service in service_status:
				if not service_status.get(service, True):
					print(f"Service {service} is not running.")
			print(FOX_START_MESSAGE)

		return are_services_running

	def run(self, site: str):
		"""Run Migrate operation on site specified. This method initializes
		and destroys connections to the site database.
		"""
		from vhtfm.utils.synchronization import filelock

		if site:
			vhtfm.init(site)
			vhtfm.connect()

		if not self.required_services_running():
			raise SystemExit(1)

		with filelock("fox_migrate", timeout=1):
			self.setUp()
			try:
				self.pre_schema_updates()
				self.run_schema_updates()
				self.post_schema_updates()
			finally:
				self.tearDown()
				vhtfm.destroy()
