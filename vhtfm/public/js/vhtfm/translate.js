// Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

// for translation
vhtfm._ = function (txt, replace, context = null) {
	if (!txt) return txt;
	if (typeof txt != "string") return txt;

	let translated_text = "";

	let key = txt; // txt.replace(/\n/g, "");
	if (context) {
		translated_text = vhtfm._messages[`${key}:${context}`];
	}

	if (!translated_text) {
		translated_text = vhtfm._messages[key] || txt;
	}

	if (replace && typeof replace === "object") {
		translated_text = $.format(translated_text, replace);
	}
	return translated_text;
};

window.__ = vhtfm._;

vhtfm.get_languages = function () {
	if (!vhtfm.languages) {
		vhtfm.languages = [];
		$.each(vhtfm.boot.lang_dict, function (lang, value) {
			vhtfm.languages.push({ label: lang, value: value });
		});
		vhtfm.languages = vhtfm.languages.sort(function (a, b) {
			return a.value < b.value ? -1 : 1;
		});
	}
	return vhtfm.languages;
};
