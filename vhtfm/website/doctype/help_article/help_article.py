# Copyright (c) 2013, Vhtfm and contributors
# License: MIT. See LICENSE

import vhtfm
from vhtfm import _
from vhtfm.rate_limiter import rate_limit
from vhtfm.utils import cint, is_markdown, markdown
from vhtfm.website.utils import get_comment_list
from vhtfm.website.website_generator import WebsiteGenerator


class HelpArticle(WebsiteGenerator):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from vhtfm.types import DF

		author: DF.Data | None
		category: DF.Link
		content: DF.TextEditor
		helpful: DF.Int
		level: DF.Literal["Beginner", "Intermediate", "Expert"]
		likes: DF.Int
		not_helpful: DF.Int
		published: DF.Check
		route: DF.Data | None
		title: DF.Data
	# end: auto-generated types

	def validate(self):
		self.set_route()

	def set_route(self):
		"""Set route from category and title if missing"""
		if not self.route:
			self.route = "/".join(
				[vhtfm.get_value("Help Category", self.category, "route"), self.scrub(self.title)]
			)

	def on_update(self):
		self.update_category()

	def clear_cache(self):
		clear_knowledge_base_cache()
		return super().clear_cache()

	def update_category(self):
		cnt = vhtfm.db.count("Help Article", filters={"category": self.category, "published": 1})
		cat = vhtfm.get_doc("Help Category", self.category)
		cat.help_articles = cnt
		cat.save()

	def get_context(self, context):
		if is_markdown(context.content):
			context.content = markdown(context.content)
		context.login_required = True
		context.category = vhtfm.get_doc("Help Category", self.category)
		context.level_class = get_level_class(self.level)
		context.comment_list = get_comment_list(self.doctype, self.name)
		context.show_sidebar = True
		context.sidebar_items = get_sidebar_items()
		context.parents = self.get_parents(context)

	def get_parents(self, context):
		return [{"title": context.category.category_name, "route": context.category.route}]


def get_list_context(context=None):
	filters = dict(published=1)

	category = vhtfm.db.get_value("Help Category", {"route": vhtfm.local.path})

	if category:
		filters["category"] = category

	list_context = vhtfm._dict(
		title=category or _("Knowledge Base"),
		get_level_class=get_level_class,
		show_sidebar=True,
		sidebar_items=get_sidebar_items(),
		hide_filters=True,
		filters=filters,
		category=vhtfm.local.form_dict.category,
		no_breadcrumbs=True,
	)

	if vhtfm.local.form_dict.txt:
		list_context.blog_subtitle = _('Filtered by "{0}"').format(vhtfm.local.form_dict.txt)
	#
	# list_context.update(vhtfm.get_doc("Blog Settings", "Blog Settings").as_dict())
	return list_context


def get_level_class(level):
	return {"Beginner": "green", "Intermediate": "orange", "Expert": "red"}[level]


def get_sidebar_items():
	def _get():
		return vhtfm.db.sql(
			"""select
				concat(category_name, " (", help_articles, ")") as title,
				concat('/', route) as route
			from
				`tabHelp Category`
			where
				published = 1 and help_articles > 0
			order by
				help_articles desc""",
			as_dict=True,
		)

	return vhtfm.cache.get_value("knowledge_base:category_sidebar", _get)


def clear_knowledge_base_cache():
	vhtfm.cache.delete_value("knowledge_base:category_sidebar")
	vhtfm.cache.delete_value("knowledge_base:faq")


@vhtfm.whitelist(allow_guest=True)
@rate_limit(key="article", limit=5, seconds=60 * 60)
def add_feedback(article: str, helpful: str):
	field = "not_helpful" if helpful == "No" else "helpful"

	value = cint(vhtfm.db.get_value("Help Article", article, field))
	vhtfm.db.set_value("Help Article", article, field, value + 1, update_modified=False)
