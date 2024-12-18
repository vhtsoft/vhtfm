import vhtfm
from vhtfm.website.page_renderers.template_page import TemplatePage


class PrintPage(TemplatePage):
	"""
	default path returns a printable object (based on permission)
	/Quotation/Q-0001
	"""

	def can_render(self):
		parts = self.path.split("/", 1)
		if len(parts) == 2:
			if vhtfm.db.exists("DocType", parts[0], True) and vhtfm.db.exists(parts[0], parts[1], True):
				return True

		return False

	def render(self):
		parts = self.path.split("/", 1)
		vhtfm.form_dict.doctype = parts[0]
		vhtfm.form_dict.name = parts[1]
		self.set_standard_path("printview")
		return super().render()
