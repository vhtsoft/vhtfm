vhtfm.provide("vhtfm.ui.misc");
vhtfm.ui.misc.about = function () {
	if (!vhtfm.ui.misc.about_dialog) {
		var d = new vhtfm.ui.Dialog({ title: __("Vhtfm Framework") });

		$(d.body).html(
			repl(
				`<div>
					<p>${__("Open Source Applications for the Web")}</p>
					<p><i class='fa fa-globe fa-fw'></i>
						${__("Website")}:
						<a href='https://vhtfmframework.com' target='_blank'>https://vhtfmframework.com</a></p>
					<p><i class='fa fa-github fa-fw'></i>
						${__("Source")}:
						<a href='https://github.com/vhtfm' target='_blank'>https://github.com/vhtfm</a></p>
					<p><i class='fa fa-graduation-cap fa-fw'></i>
						Vhtfm School: <a href='https://vhtfm.school' target='_blank'>https://vhtfm.school</a></p>
					<p><i class='fa fa-linkedin fa-fw'></i>
						Linkedin: <a href='https://linkedin.com/company/vhtfm-tech' target='_blank'>https://linkedin.com/company/vhtfm-tech</a></p>
					<p><i class='fa fa-twitter fa-fw'></i>
						Twitter: <a href='https://twitter.com/vhtfmtech' target='_blank'>https://twitter.com/vhtfmtech</a></p>
					<p><i class='fa fa-youtube fa-fw'></i>
						YouTube: <a href='https://www.youtube.com/@vhtfmtech' target='_blank'>https://www.youtube.com/@vhtfmtech</a></p>
					<hr>
					<h4>${__("Installed Apps")}</h4>
					<div id='about-app-versions'>${__("Loading versions...")}</div>
					<p>
						<b>
							<a href="/attribution" target="_blank" class="text-muted">
								${__("Dependencies & Licenses")}
							</a>
						</b>
					</p>
					<hr>
					<p class='text-muted'>${__("&copy; Vhtfm Technologies Pvt. Ltd. and contributors")} </p>
					</div>`,
				vhtfm.app
			)
		);

		vhtfm.ui.misc.about_dialog = d;

		vhtfm.ui.misc.about_dialog.on_page_show = function () {
			if (!vhtfm.versions) {
				vhtfm.call({
					method: "vhtfm.utils.change_log.get_versions",
					callback: function (r) {
						show_versions(r.message);
					},
				});
			} else {
				show_versions(vhtfm.versions);
			}
		};

		var show_versions = function (versions) {
			var $wrap = $("#about-app-versions").empty();
			$.each(Object.keys(versions).sort(), function (i, key) {
				var v = versions[key];
				let text;
				if (v.branch) {
					text = $.format("<p><b>{0}:</b> v{1} ({2})<br></p>", [
						v.title,
						v.branch_version || v.version,
						v.branch,
					]);
				} else {
					text = $.format("<p><b>{0}:</b> v{1}<br></p>", [v.title, v.version]);
				}
				$(text).appendTo($wrap);
			});

			vhtfm.versions = versions;
		};
	}

	vhtfm.ui.misc.about_dialog.show();
};
