import vhtfm
from vhtfm.utils import cint

# This patch aims to apply & delete all the customization
# on custom doctypes done through customize form

# This is required because customize form in now blocked
# for custom doctypes and user may not be able to
# see previous customization


def execute():
	custom_doctypes = vhtfm.get_all("DocType", filters={"custom": 1})

	for doctype in custom_doctypes:
		property_setters = vhtfm.get_all(
			"Property Setter",
			filters={"doc_type": doctype.name, "doctype_or_field": "DocField"},
			fields=["name", "property", "value", "property_type", "field_name"],
		)

		custom_fields = vhtfm.get_all("Custom Field", filters={"dt": doctype.name}, fields=["*"])

		property_setter_map = {}

		for prop in property_setters:
			property_setter_map[prop.field_name] = prop
			vhtfm.db.delete("Property Setter", {"name": prop.name})

		meta = vhtfm.get_meta(doctype.name)

		for df in meta.fields:
			ps = property_setter_map.get(df.fieldname, None)
			if ps:
				value = cint(ps.value) if ps.property_type == "Int" else ps.value
				df.set(ps.property, value)

		for cf in custom_fields:
			cf.pop("parenttype")
			cf.pop("parentfield")
			cf.pop("parent")
			cf.pop("name")
			field = meta.get_field(cf.fieldname)
			if field:
				field.update(cf)
			else:
				df = vhtfm.new_doc("DocField", parent_doc=meta, parentfield="fields")
				df.update(cf)
				meta.fields.append(df)
			vhtfm.db.delete("Custom Field", {"name": cf.name})

		meta.save()
