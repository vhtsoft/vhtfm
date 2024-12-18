# Copyright (c) 2021, Vhtfm Technologies Pvt. Ltd. and Contributors
# MIT License. See LICENSE
"""
vhtfm.coverage
~~~~~~~~~~~~~~~~

Coverage settings for vhtfm
"""

STANDARD_INCLUSIONS = ["*.py"]

STANDARD_EXCLUSIONS = [
	"*.js",
	"*.xml",
	"*.pyc",
	"*.css",
	"*.less",
	"*.scss",
	"*.vue",
	"*.html",
	"*/test_*",
	"*/node_modules/*",
	"*/doctype/*/*_dashboard.py",
	"*/patches/*",
]

# tested via commands' test suite
TESTED_VIA_CLI = [
	"*/vhtfm/installer.py",
	"*/vhtfm/utils/install.py",
	"*/vhtfm/utils/scheduler.py",
	"*/vhtfm/utils/doctor.py",
	"*/vhtfm/build.py",
	"*/vhtfm/database/__init__.py",
	"*/vhtfm/database/db_manager.py",
	"*/vhtfm/database/**/setup_db.py",
]

VHTFM_EXCLUSIONS = [
	"*/tests/*",
	"*/commands/*",
	"*/vhtfm/change_log/*",
	"*/vhtfm/exceptions*",
	"*/vhtfm/desk/page/setup_wizard/setup_wizard.py",
	"*/vhtfm/coverage.py",
	"*vhtfm/setup.py",
	"*/doctype/*/*_dashboard.py",
	"*/patches/*",
	*TESTED_VIA_CLI,
]


class CodeCoverage:
	"""
	Context manager for handling code coverage.

	This class sets up code coverage measurement for a specific app,
	applying the appropriate inclusion and exclusion patterns.
	"""

	def __init__(self, with_coverage, app, outfile="coverage.xml"):
		self.with_coverage = with_coverage
		self.app = app or "vhtfm"
		self.outfile = outfile

	def __enter__(self):
		if self.with_coverage:
			import os

			from coverage import Coverage

			from vhtfm.utils import get_fox_path

			# Generate coverage report only for app that is being tested
			source_path = os.path.join(get_fox_path(), "apps", self.app)
			omit = STANDARD_EXCLUSIONS[:]

			if self.app == "vhtfm":
				omit.extend(VHTFM_EXCLUSIONS)

			self.coverage = Coverage(source=[source_path], omit=omit, include=STANDARD_INCLUSIONS)
			self.coverage.start()
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		if self.with_coverage:
			self.coverage.stop()
			self.coverage.save()
			self.coverage.xml_report(outfile=self.outfile)
			print("Saved Coverage")
