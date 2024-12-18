import vhtfm
from vhtfm import _
from vhtfm.utils import cstr
from vhtfm.website.page_renderers.template_page import TemplatePage


class NotPermittedPage(TemplatePage):
	def __init__(self, path=None, http_status_code=None, exception=""):
		vhtfm.local.message = cstr(exception)
		super().__init__(path=path, http_status_code=http_status_code)
		self.http_status_code = 403

	def can_render(self):
		return True

	def render(self):
		action = f"/login?redirect-to={vhtfm.request.path}"
		if vhtfm.request.path.startswith("/app/") or vhtfm.request.path == "/app":
			action = "/login"
		vhtfm.local.message_title = _("Not Permitted")
		vhtfm.local.response["context"] = dict(
			indicator_color="red", primary_action=action, primary_label=_("Login"), fullpage=True
		)
		self.set_standard_path("message")
		return super().render()
