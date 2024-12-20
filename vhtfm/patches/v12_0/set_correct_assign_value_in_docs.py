import vhtfm
from vhtfm.query_builder.functions import Coalesce, GroupConcat


def execute():
	vhtfm.reload_doc("desk", "doctype", "todo")

	ToDo = vhtfm.qb.DocType("ToDo")
	assignees = GroupConcat("owner").distinct().as_("assignees")

	assignments = (
		vhtfm.qb.from_(ToDo)
		.select(ToDo.name, ToDo.reference_type, assignees)
		.where(Coalesce(ToDo.reference_type, "") != "")
		.where(Coalesce(ToDo.reference_name, "") != "")
		.where(ToDo.status != "Cancelled")
		.groupby(ToDo.reference_type, ToDo.reference_name)
	).run(as_dict=True)

	for doc in assignments:
		assignments = doc.assignees.split(",")
		vhtfm.db.set_value(
			doc.reference_type,
			doc.reference_name,
			"_assign",
			vhtfm.as_json(assignments),
			update_modified=False,
		)
