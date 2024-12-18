// Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

vhtfm.provide("vhtfm.help");

vhtfm.help.youtube_id = {};

vhtfm.help.has_help = function (doctype) {
	return vhtfm.help.youtube_id[doctype];
};

vhtfm.help.show = function (doctype) {
	if (vhtfm.help.youtube_id[doctype]) {
		vhtfm.help.show_video(vhtfm.help.youtube_id[doctype]);
	}
};

vhtfm.help.show_video = function (youtube_id, title) {
	if (vhtfm.utils.is_url(youtube_id)) {
		const expression =
			'(?:youtube.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu.be/)([^"&?\\s]{11})';
		youtube_id = youtube_id.match(expression)[1];
	}

	// (vhtfm.help_feedback_link || "")
	let dialog = new vhtfm.ui.Dialog({
		title: title || __("Help"),
		size: "large",
	});

	let video = $(
		`<div class="video-player" data-plyr-provider="youtube" data-plyr-embed-id="${youtube_id}"></div>`
	);
	video.appendTo(dialog.body);

	dialog.show();
	dialog.$wrapper.addClass("video-modal");

	let plyr;
	vhtfm.utils.load_video_player().then(() => {
		plyr = new vhtfm.Plyr(video[0], {
			hideControls: true,
			resetOnEnd: true,
		});
	});

	dialog.onhide = () => {
		plyr?.destroy();
	};
};

$("body").on("click", "a.help-link", function () {
	var doctype = $(this).attr("data-doctype");
	doctype && vhtfm.help.show(doctype);
});
