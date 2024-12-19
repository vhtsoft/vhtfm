# Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
def get_jenv():
	import vhtfm

	if not getattr(vhtfm.local, "jenv", None):
		from jinja2 import DebugUndefined
		from jinja2.sandbox import SandboxedEnvironment

		from vhtfm.utils.safe_exec import UNSAFE_ATTRIBUTES, get_safe_globals

		UNSAFE_ATTRIBUTES = UNSAFE_ATTRIBUTES - {"format", "format_map"}

		class VhtfmSandboxedEnvironment(SandboxedEnvironment):
			def is_safe_attribute(self, obj, attr, *args, **kwargs):
				if attr in UNSAFE_ATTRIBUTES:
					return False

				return super().is_safe_attribute(obj, attr, *args, **kwargs)

		# vhtfm will be loaded last, so app templates will get precedence
		jenv = VhtfmSandboxedEnvironment(loader=get_jloader(), undefined=DebugUndefined)
		set_filters(jenv)

		jenv.globals.update(get_safe_globals())

		methods, filters = get_jinja_hooks()
		jenv.globals.update(methods or {})
		jenv.filters.update(filters or {})

		vhtfm.local.jenv = jenv

	return vhtfm.local.jenv


def get_template(path):
	return get_jenv().get_template(path)


def get_email_from_template(name, args):
	from jinja2 import TemplateNotFound

	args = args or {}
	try:
		message = get_template("templates/emails/" + name + ".html").render(args)
	except TemplateNotFound as e:
		raise e

	try:
		text_content = get_template("templates/emails/" + name + ".txt").render(args)
	except TemplateNotFound:
		text_content = None

	return (message, text_content)


def validate_template(html):
	"""Throws exception if there is a syntax error in the Jinja Template"""
	from jinja2 import TemplateSyntaxError

	import vhtfm

	if not html:
		return
	jenv = get_jenv()
	try:
		jenv.from_string(html)
	except TemplateSyntaxError as e:
		vhtfm.throw(f"Syntax error in template as line {e.lineno}: {e.message}")


def render_template(template, context=None, is_path=None, safe_render=True):
	"""Render a template using Jinja

	:param template: path or HTML containing the jinja template
	:param context: dict of properties to pass to the template
	:param is_path: (optional) assert that the `template` parameter is a path
	:param safe_render: (optional) prevent server side scripting via jinja templating
	"""
	if not template:
		return ""

	from jinja2 import TemplateError
	from jinja2.sandbox import SandboxedEnvironment

	from vhtfm import _, get_traceback, throw

	if context is None:
		context = {}

	jenv: SandboxedEnvironment = get_jenv()
	if is_path or guess_is_path(template):
		is_path = True
		compiled_template = jenv.get_template(template)
	else:
		if safe_render and ".__" in template:
			throw(_("Illegal template"))
		try:
			compiled_template = jenv.from_string(template)
		except TemplateError:
			import html

			throw(
				title="Jinja Template Error",
				msg=f"<pre>{template}</pre><pre>{html.escape(get_traceback())}</pre>",
			)

	import time

	from vhtfm.utils.logger import get_logger

	logger = get_logger("render-template")
	try:
		start_time = time.monotonic()
		return compiled_template.render(context)
	except Exception as e:
		import html

		throw(title="Context Error", msg=f"<pre>{html.escape(get_traceback())}</pre>", exc=e)
	finally:
		if is_path:
			logger.debug(f"Rendering time: {time.monotonic() - start_time:.6f} seconds ({template})")
		else:
			logger.debug(f"Rendering time: {time.monotonic() - start_time:.6f} seconds")


def guess_is_path(template):
	# template can be passed as a path or content
	# if its single line and ends with a html, then its probably a path
	if "\n" not in template and "." in template:
		extn = template.rsplit(".")[-1]
		if extn in ("html", "css", "scss", "py", "md", "json", "js", "xml", "txt"):
			return True

	return False


def get_jloader():
	import vhtfm

	if not getattr(vhtfm.local, "jloader", None):
		from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader

		apps = vhtfm.get_hooks("template_apps")
		if not apps:
			apps = list(
				reversed(
					vhtfm.local.flags.web_pages_apps or vhtfm.get_installed_apps(_ensure_on_fox=True)
				)
			)

		if "vhtfm" not in apps:
			apps.append("vhtfm")

		vhtfm.local.jloader = ChoiceLoader(
			# search for something like app/templates/...
			[PrefixLoader({app: PackageLoader(app, ".") for app in apps})]
			# search for something like templates/...
			+ [PackageLoader(app, ".") for app in apps]
		)

	return vhtfm.local.jloader


def set_filters(jenv):
	import vhtfm
	from vhtfm.utils import cint, cstr, flt

	jenv.filters.update(
		{
			"json": vhtfm.as_json,
			"len": len,
			"int": cint,
			"str": cstr,
			"flt": flt,
		}
	)


def get_jinja_hooks():
	"""Return a tuple of (methods, filters) each containing a dict of method name and method definition pair."""
	import vhtfm

	if not getattr(vhtfm.local, "site", None):
		return (None, None)

	from inspect import getmembers, isfunction
	from types import FunctionType, ModuleType

	def get_obj_dict_from_paths(object_paths):
		out = {}
		for obj_path in object_paths:
			try:
				obj = vhtfm.get_module(obj_path)
			except ModuleNotFoundError:
				obj = vhtfm.get_attr(obj_path)

			if isinstance(obj, ModuleType):
				functions = getmembers(obj, isfunction)
				for function_name, function in functions:
					out[function_name] = function
			elif isinstance(obj, FunctionType):
				function_name = obj.__name__
				out[function_name] = obj
		return out

	values = vhtfm.get_hooks("jinja")
	methods, filters = values.get("methods", []), values.get("filters", [])

	method_dict = get_obj_dict_from_paths(methods)
	filter_dict = get_obj_dict_from_paths(filters)

	return method_dict, filter_dict