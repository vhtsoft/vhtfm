# Copyright (c) 2020, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import datetime
import json
import os
import traceback
import uuid

import rq

import vhtfm
from vhtfm.utils.data import cint

MONITOR_REDIS_KEY = "monitor-transactions"
MONITOR_MAX_ENTRIES = 1000000


def start(transaction_type="request", method=None, kwargs=None):
	if vhtfm.conf.monitor:
		vhtfm.local.monitor = Monitor(transaction_type, method, kwargs)


def stop(response=None):
	if hasattr(vhtfm.local, "monitor"):
		vhtfm.local.monitor.dump(response)


def add_data_to_monitor(**kwargs) -> None:
	"""Add additional custom key-value pairs along with monitor log.
	Note: Key-value pairs should be simple JSON exportable types."""
	if hasattr(vhtfm.local, "monitor"):
		vhtfm.local.monitor.add_custom_data(**kwargs)


def get_trace_id() -> str | None:
	"""Get unique ID for current transaction."""
	if monitor := getattr(vhtfm.local, "monitor", None):
		return monitor.data.uuid


def log_file():
	return os.path.join(vhtfm.utils.get_fox_path(), "logs", "monitor.json.log")


class Monitor:
	__slots__ = ("data",)

	def __init__(self, transaction_type, method, kwargs):
		try:
			self.data = vhtfm._dict(
				{
					"site": vhtfm.local.site,
					"timestamp": datetime.datetime.now(datetime.timezone.utc),
					"transaction_type": transaction_type,
					"uuid": str(uuid.uuid4()),
				}
			)

			if transaction_type == "request":
				self.collect_request_meta()
			else:
				self.collect_job_meta(method, kwargs)
		except Exception:
			traceback.print_exc()

	def collect_request_meta(self):
		self.data.request = vhtfm._dict(
			{
				"ip": vhtfm.local.request_ip,
				"method": vhtfm.request.method,
				"path": vhtfm.request.path,
			}
		)

		if request_id := vhtfm.request.headers.get("X-Vhtfm-Request-Id"):
			self.data.uuid = request_id

	def collect_job_meta(self, method, kwargs):
		self.data.job = vhtfm._dict({"method": method, "scheduled": False, "wait": 0})
		if "run_scheduled_job" in method:
			self.data.job.method = kwargs["job_type"]
			self.data.job.scheduled = True

		if job := rq.get_current_job():
			self.data.uuid = job.id
			waitdiff = self.data.timestamp - job.enqueued_at.replace(tzinfo=datetime.timezone.utc)
			self.data.job.wait = int(waitdiff.total_seconds() * 1000000)

	def add_custom_data(self, **kwargs):
		if self.data:
			self.data.update(kwargs)

	def dump(self, response=None):
		try:
			timediff = datetime.datetime.now(datetime.timezone.utc) - self.data.timestamp
			# Obtain duration in microseconds
			self.data.duration = int(timediff.total_seconds() * 1000000)

			if self.data.transaction_type == "request":
				if response:
					self.data.request.status_code = response.status_code
					self.data.request.response_length = int(response.headers.get("Content-Length", 0))
				else:
					self.data.request.status_code = 500

				if hasattr(vhtfm.local, "rate_limiter"):
					limiter = vhtfm.local.rate_limiter
					self.data.request.counter = limiter.counter
					if limiter.rejected:
						self.data.request.reset = limiter.reset

			self.store()
		except Exception:
			traceback.print_exc()

	def store(self):
		serialized = json.dumps(self.data, sort_keys=True, default=str, separators=(",", ":"))
		length = vhtfm.cache.rpush(MONITOR_REDIS_KEY, serialized)
		if cint(length) > MONITOR_MAX_ENTRIES:
			vhtfm.cache.ltrim(MONITOR_REDIS_KEY, 1, -1)


def flush():
	try:
		# Fetch all the logs without removing from cache
		logs = vhtfm.cache.lrange(MONITOR_REDIS_KEY, 0, -1)
		if logs:
			logs = list(map(vhtfm.safe_decode, logs))
			with open(log_file(), "a", os.O_NONBLOCK) as f:
				f.write("\n".join(logs))
				f.write("\n")
			# Remove fetched entries from cache
			vhtfm.cache.ltrim(MONITOR_REDIS_KEY, len(logs) - 1, -1)
	except Exception:
		traceback.print_exc()