// Copyright (c) 2024, Vhtfm Technologies and contributors
// For license information, please see license.txt

vhtfm.ui.form.on("Role Replication", {
	refresh(frm) {
		frm.disable_save();
		frm.page.set_primary_action(__("Replicate"), ($btn) => {
			$btn.text(__("Replicating..."));
			vhtfm.run_serially([
				() => vhtfm.dom.freeze("Replicating..."),
				() => frm.call("replicate_role"),
				() => vhtfm.dom.unfreeze(),
				() => vhtfm.msgprint(__("Replication completed.")),
				() => $btn.text(__("Replicate")),
			]);
		});
	},
});
