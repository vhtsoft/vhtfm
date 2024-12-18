context.skip("Permissions API", () => {
	before(() => {
		cy.visit("/login");
		cy.remove_role("vhtfm@example.com", "System Manager");
		cy.visit("/app");
	});

	it("Checks permissions via `has_perm` for Kanban Board DocType", () => {
		cy.visit("/app/kanban-board/view/list");
		cy.window()
			.its("vhtfm")
			.then((vhtfm) => {
				vhtfm.model.with_doctype("Kanban Board", function () {
					// needed to make sure doc meta is loaded
					expect(vhtfm.perm.has_perm("Kanban Board", 0, "read")).to.equal(true);
					expect(vhtfm.perm.has_perm("Kanban Board", 0, "write")).to.equal(true);
					expect(vhtfm.perm.has_perm("Kanban Board", 0, "print")).to.equal(false);
				});
			});
	});

	it("Checks permissions via `get_perm` for Kanban Board DocType", () => {
		cy.visit("/app/kanban-board/view/list");
		cy.window()
			.its("vhtfm")
			.then((vhtfm) => {
				vhtfm.model.with_doctype("Kanban Board", function () {
					// needed to make sure doc meta is loaded
					const perms = vhtfm.perm.get_perm("Kanban Board");
					expect(perms.read).to.equal(true);
					expect(perms.write).to.equal(true);
					expect(perms.rights_without_if_owner).to.include("read");
				});
			});
	});

	after(() => {
		cy.add_role("vhtfm@example.com", "System Manager");
		cy.call("logout");
	});
});
