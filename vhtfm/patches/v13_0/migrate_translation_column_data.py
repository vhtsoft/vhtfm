import vhtfm


def execute():
	vhtfm.reload_doctype("Translation")
	vhtfm.db.sql(
		"UPDATE `tabTranslation` SET `translated_text`=`target_name`, `source_text`=`source_name`, `contributed`=0"
	)
