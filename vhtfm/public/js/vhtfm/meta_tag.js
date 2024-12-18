vhtfm.provide("vhtfm.model");
vhtfm.provide("vhtfm.utils");

/**
 * Opens the Website Meta Tag form if it exists for {route}
 * or creates a new doc and opens the form
 */
vhtfm.utils.set_meta_tag = function (route) {
	vhtfm.db.exists("Website Route Meta", route).then((exists) => {
		if (exists) {
			vhtfm.set_route("Form", "Website Route Meta", route);
		} else {
			// new doc
			const doc = vhtfm.model.get_new_doc("Website Route Meta");
			doc.__newname = route;
			vhtfm.set_route("Form", doc.doctype, doc.name);
		}
	});
};
