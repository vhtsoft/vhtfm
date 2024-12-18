# Copyright (c) 2021, Vhtfm Technologies and contributors
# For license information, please see license.txt

import vhtfm
from vhtfm import _
from vhtfm.model.document import Document


class NetworkPrinterSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from vhtfm.types import DF

		port: DF.Int
		printer_name: DF.Literal[None]
		server_ip: DF.Data
	# end: auto-generated types

	@vhtfm.whitelist()
	def get_printers_list(self, ip="127.0.0.1", port=631):
		printer_list = []
		try:
			import cups
		except ImportError:
			vhtfm.throw(
				_(
					"""This feature can not be used as dependencies are missing.
				Please contact your system manager to enable this by installing pycups!"""
				)
			)
			return
		try:
			cups.setServer(self.server_ip)
			cups.setPort(self.port)
			conn = cups.Connection()
			printers = conn.getPrinters()
			printer_list.extend(
				{"value": printer_id, "label": printer["printer-make-and-model"]}
				for printer_id, printer in printers.items()
			)
		except RuntimeError:
			vhtfm.throw(_("Failed to connect to server"))
		except vhtfm.ValidationError:
			vhtfm.throw(_("Failed to connect to server"))
		return printer_list


@vhtfm.whitelist()
def get_network_printer_settings():
	return vhtfm.db.get_list("Network Printer Settings", pluck="name")
