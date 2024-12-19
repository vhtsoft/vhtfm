// Copyright (c) 2015, Vhtfm Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

// My HTTP Request

vhtfm.provide("vhtfm.request");
vhtfm.provide("vhtfm.request.error_handlers");
vhtfm.request.url = "/";
vhtfm.request.ajax_count = 0;
vhtfm.request.waiting_for_ajax = [];
vhtfm.request.logs = {};

vhtfm.xcall = function (method, params, type) {
	return new Promise((resolve, reject) => {
		vhtfm.call({
			method: method,
			args: params,
			type: type || "POST",
			callback: (r) => {
				resolve(r.message);
			},
			error: (r) => {
				reject(r?.message);
			},
		});
	});
};

// generic server call (call page, object)
vhtfm.call = function (opts) {
	if (!vhtfm.is_online()) {
		vhtfm.show_alert(
			{
				indicator: "orange",
				message: __("Connection Lost"),
				subtitle: __("You are not connected to Internet. Retry after sometime."),
			},
			3
		);
		opts.always && opts.always();
		return $.ajax();
	}
	if (typeof arguments[0] === "string") {
		opts = {
			method: arguments[0],
			args: arguments[1],
			callback: arguments[2],
			headers: arguments[3],
		};
	}

	if (opts.quiet) {
		opts.no_spinner = true;
	}
	var args = $.extend({}, opts.args);

	if (args.freeze) {
		opts.freeze = opts.freeze || args.freeze;
		opts.freeze_message = opts.freeze_message || args.freeze_message;
	}

	// cmd
	if (opts.module && opts.page) {
		args.cmd = opts.module + ".page." + opts.page + "." + opts.page + "." + opts.method;
	} else if (opts.doc) {
		$.extend(args, {
			cmd: "run_doc_method",
			docs: vhtfm.get_doc(opts.doc.doctype, opts.doc.name),
			method: opts.method,
			args: opts.args,
		});
	} else if (opts.method) {
		args.cmd = opts.method;
	}

	var callback = function (data, response_text) {
		if (data.task_id) {
			// async call, subscribe
			vhtfm.realtime.subscribe(data.task_id, opts);

			if (opts.queued) {
				opts.queued(data);
			}
		} else if (opts.callback) {
			// ajax
			return opts.callback(data, response_text);
		}
	};

	let url = opts.url;
	if (!url) {
		let prefix = "/api/method/";
		if (opts.api_version) {
			prefix = `/api/${opts.api_version}/method/`;
		}
		url = prefix + args.cmd;
		if (window.cordova) {
			let host = vhtfm.request.url;
			host = host.slice(0, host.length - 1);
			url = host + url;
		}
		delete args.cmd;
	}

	// debouce if required
	if (opts.debounce && vhtfm.request.is_fresh(args, opts.debounce)) {
		return Promise.resolve();
	}

	return vhtfm.request.call({
		type: opts.type || "POST",
		args: args,
		success: callback,
		error: opts.error,
		always: opts.always,
		btn: opts.btn,
		freeze: opts.freeze,
		freeze_message: opts.freeze_message,
		headers: opts.headers || {},
		error_handlers: opts.error_handlers || {},
		// show_spinner: !opts.no_spinner,
		async: opts.async,
		silent: opts.silent,
		api_version: opts.api_version,
		url,
	});
};

vhtfm.request.call = function (opts) {
	vhtfm.request.prepare(opts);

	var statusCode = {
		200: function (data, xhr) {
			opts.success_callback && opts.success_callback(data, xhr.responseText);
		},
		401: function (xhr) {
			if (vhtfm.app.session_expired_dialog && vhtfm.app.session_expired_dialog.display) {
				vhtfm.app.redirect_to_login();
			} else {
				vhtfm.app.handle_session_expired();
			}
			opts.error_callback && opts.error_callback();
		},
		404: function (xhr) {
			vhtfm.msgprint({
				title: __("Not found"),
				indicator: "red",
				message: __("The resource you are looking for is not available"),
			});
			opts.error_callback && opts.error_callback();
		},
		403: function (xhr) {
			if (vhtfm.session.user === "Guest" && vhtfm.session.logged_in_user !== "Guest") {
				// session expired
				vhtfm.app.handle_session_expired();
			} else if (xhr.responseJSON && xhr.responseJSON._error_message) {
				vhtfm.msgprint({
					title: __("Not permitted"),
					indicator: "red",
					message: xhr.responseJSON._error_message,
				});

				xhr.responseJSON._server_messages = null;
			} else if (xhr.responseJSON && xhr.responseJSON._server_messages) {
				var _server_messages = JSON.parse(xhr.responseJSON._server_messages);

				// avoid double messages
				if (_server_messages.indexOf(__("Not permitted")) !== -1) {
					return;
				}
			} else {
				vhtfm.msgprint({
					title: __("Not permitted"),
					indicator: "red",
					message: __(
						"You do not have enough permissions to access this resource. Please contact your manager to get access."
					),
				});
			}
			opts.error_callback && opts.error_callback();
		},
		508: function (xhr) {
			vhtfm.utils.play_sound("error");
			vhtfm.msgprint({
				title: __("Please try again"),
				indicator: "red",
				message: __(
					"Another transaction is blocking this one. Please try again in a few seconds."
				),
			});
			opts.error_callback && opts.error_callback();
		},
		413: function (data, xhr) {
			vhtfm.msgprint({
				indicator: "red",
				title: __("File too big"),
				message: __("File size exceeded the maximum allowed size of {0} MB", [
					(vhtfm.boot.max_file_size || 5242880) / 1048576,
				]),
			});
			opts.error_callback && opts.error_callback();
		},
		417: function (xhr) {
			var r = xhr.responseJSON;
			if (!r) {
				try {
					r = JSON.parse(xhr.responseText);
				} catch (e) {
					r = xhr.responseText;
				}
			}

			opts.error_callback && opts.error_callback(r);
		},
		501: function (data, xhr) {
			if (typeof data === "string") data = JSON.parse(data);
			opts.error_callback && opts.error_callback(data, xhr.responseText);
		},
		500: function (xhr) {
			vhtfm.utils.play_sound("error");
			try {
				opts.error_callback && opts.error_callback();
				vhtfm.request.report_error(xhr, opts);
			} catch (e) {
				vhtfm.request.report_error(xhr, opts);
			}
		},
		504: function (xhr) {
			vhtfm.msgprint(__("Request Timed Out"));
			opts.error_callback && opts.error_callback();
		},
		502: function (xhr) {
			vhtfm.msgprint(__("Internal Server Error"));
			opts.error_callback && opts.error_callback();
		},
	};

	var exception_handlers = {
		QueryTimeoutError: function () {
			vhtfm.utils.play_sound("error");
			vhtfm.msgprint({
				title: __("Request Timeout"),
				indicator: "red",
				message: __("Server was too busy to process this request. Please try again."),
			});
		},
		QueryDeadlockError: function () {
			vhtfm.utils.play_sound("error");
			vhtfm.msgprint({
				title: __("Deadlock Occurred"),
				indicator: "red",
				message: __("Server was too busy to process this request. Please try again."),
			});
		},
	};

	var ajax_args = {
		url: opts.url || vhtfm.request.url,
		data: opts.args,
		type: opts.type,
		dataType: opts.dataType || "json",
		async: opts.async,
		headers: Object.assign(
			{
				"X-Vhtfm-CSRF-Token": vhtfm.csrf_token,
				Accept: "application/json",
				"X-Vhtfm-CMD": (opts.args && opts.args.cmd) || "" || "",
			},
			opts.headers
		),
		cache: window.dev_server ? false : true,
	};

	if (opts.args && opts.args.doctype) {
		ajax_args.headers["X-Vhtfm-Doctype"] = encodeURIComponent(opts.args.doctype);
	}

	vhtfm.last_request = ajax_args.data;

	return $.ajax(ajax_args)
		.done(function (data, textStatus, xhr) {
			try {
				if (typeof data === "string") data = JSON.parse(data);

				// sync attached docs
				if (data.docs || data.docinfo) {
					vhtfm.model.sync(data);
				}

				// sync translated messages
				if (data.__messages) {
					$.extend(vhtfm._messages, data.__messages);
				}

				// sync link titles
				if (data._link_titles) {
					if (!vhtfm._link_titles) {
						vhtfm._link_titles = {};
					}
					$.extend(vhtfm._link_titles, data._link_titles);
				}

				// callbacks
				var status_code_handler = statusCode[xhr.statusCode().status];
				if (status_code_handler) {
					status_code_handler(data, xhr);
				}
			} catch (e) {
				console.log("Unable to handle success response", data);
				console.error(e);
			}
		})
		.always(function (data, textStatus, xhr) {
			try {
				if (typeof data === "string") {
					data = JSON.parse(data);
				}
				if (data.responseText) {
					var xhr = data; // eslint-disable-line
					data = JSON.parse(data.responseText);
				}
			} catch (e) {
				data = null;
				// pass
			}
			vhtfm.request.cleanup(opts, data);
			if (opts.always) {
				opts.always(data);
			}
		})
		.fail(function (xhr, textStatus) {
			try {
				if (
					xhr.getResponseHeader("content-type") == "application/json" &&
					xhr.responseText
				) {
					var data;
					try {
						data = JSON.parse(xhr.responseText);
					} catch (e) {
						console.log("Unable to parse reponse text");
						console.log(xhr.responseText);
						console.log(e);
					}
					if (data && data.exception) {
						// vhtfm.exceptions.CustomError: (1024, ...) -> CustomError
						var exception = data.exception.split(".").at(-1).split(":").at(0);
						var exception_handler = exception_handlers[exception];
						if (exception_handler) {
							exception_handler(data);
							return;
						}
					}
				}
				var status_code_handler = statusCode[xhr.statusCode().status];
				if (status_code_handler) {
					status_code_handler(xhr);
					return;
				}
				// if not handled by error handler!
				opts.error_callback && opts.error_callback(xhr);
			} catch (e) {
				console.log("Unable to handle failed response");
				console.error(e);
			}
		});
};

vhtfm.request.is_fresh = function (args, threshold) {
	// return true if a request with similar args has been sent recently
	if (!vhtfm.request.logs[args.cmd]) {
		vhtfm.request.logs[args.cmd] = [];
	}

	for (let past_request of vhtfm.request.logs[args.cmd]) {
		// check if request has same args and was made recently
		if (
			new Date() - past_request.timestamp < threshold &&
			vhtfm.utils.deep_equal(args, past_request.args)
		) {
			console.log("throttled");
			return true;
		}
	}

	// log the request
	vhtfm.request.logs[args.cmd].push({ args: args, timestamp: new Date() });
	return false;
};

// call execute serverside request
vhtfm.request.prepare = function (opts) {
	$("body").attr("data-ajax-state", "triggered");

	// btn indicator
	if (opts.btn) $(opts.btn).prop("disabled", true);

	// freeze page
	if (opts.freeze) vhtfm.dom.freeze(opts.freeze_message);

	// stringify args if required
	for (var key in opts.args) {
		if (opts.args[key] && ($.isPlainObject(opts.args[key]) || $.isArray(opts.args[key]))) {
			opts.args[key] = JSON.stringify(opts.args[key]);
		}
	}

	// no cmd?
	if (!opts.args.cmd && !opts.url) {
		console.log(opts);
		throw "Incomplete Request";
	}

	opts.success_callback = opts.success;
	opts.error_callback = opts.error;
	delete opts.success;
	delete opts.error;
};

vhtfm.request.cleanup = function (opts, r) {
	// stop button indicator
	if (opts.btn) {
		$(opts.btn).prop("disabled", false);
	}

	$("body").attr("data-ajax-state", "complete");

	// un-freeze page
	if (opts.freeze) vhtfm.dom.unfreeze();

	if (r) {
		// session expired? - Guest has no business here!
		if (
			r.session_expired ||
			(vhtfm.session.user === "Guest" && vhtfm.session.logged_in_user !== "Guest")
		) {
			vhtfm.app.handle_session_expired();
			return;
		}

		// error handlers
		let global_handlers = vhtfm.request.error_handlers[r.exc_type] || [];
		let request_handler = opts.error_handlers ? opts.error_handlers[r.exc_type] : null;
		let handlers = [].concat(global_handlers, request_handler).filter(Boolean);

		if (r.exc_type) {
			handlers.forEach((handler) => {
				handler(r);
			});
		}

		// show messages
		//
		let messages;
		if (opts.api_version == "v2") {
			messages = r.messages;
		} else if (r._server_messages) {
			messages = JSON.parse(r._server_messages);
		}
		if (messages && !opts.silent) {
			// show server messages if no handlers exist
			if (handlers.length === 0) {
				vhtfm.hide_msgprint();
				vhtfm.msgprint(messages);
			}
		}

		// show errors
		if (r.exc) {
			r.exc = JSON.parse(r.exc);
			if (r.exc instanceof Array) {
				r.exc.forEach((exc) => {
					if (exc) {
						console.error(exc);
					}
				});
			} else {
				console.error(r.exc);
			}
		}

		// debug messages
		if (r._debug_messages) {
			if (opts.args) {
				console.log("======== arguments ========");
				console.log(opts.args);
			}
			console.log("======== debug messages ========");
			$.each(JSON.parse(r._debug_messages), function (i, v) {
				console.log(v);
			});
			console.log("======== response ========");
			delete r._debug_messages;
			console.log(r);
			console.log("========");
		}
	}

	vhtfm.last_response = r;
};

vhtfm.after_server_call = () => {
	if (vhtfm.request.ajax_count) {
		return new Promise((resolve) => {
			vhtfm.request.waiting_for_ajax.push(() => {
				resolve();
			});
		});
	} else {
		return null;
	}
};

vhtfm.after_ajax = function (fn) {
	return new Promise((resolve) => {
		if (vhtfm.request.ajax_count) {
			vhtfm.request.waiting_for_ajax.push(() => {
				if (fn) return resolve(fn());
				resolve();
			});
		} else {
			if (fn) return resolve(fn());
			resolve();
		}
	});
};

vhtfm.request.report_error = function (xhr, request_opts) {
	var data = JSON.parse(xhr.responseText);
	var exc;
	if (data.exc) {
		try {
			exc = (JSON.parse(data.exc) || []).join("\n");
		} catch (e) {
			exc = data.exc;
		}
		delete data.exc;
	} else {
		exc = "";
	}

	const copy_markdown_to_clipboard = () => {
		const code_block = (snippet) => "```\n" + snippet + "\n```";

		let request_data = Object.assign({}, request_opts);
		request_data.request_id = xhr.getResponseHeader("X-Vhtfm-Request-Id");
		const traceback_info = [
			"### App Versions",
			code_block(JSON.stringify(vhtfm.boot.versions, null, "\t")),
			"### Route",
			code_block(vhtfm.get_route_str()),
			"### Traceback",
			code_block(exc),
			"### Request Data",
			code_block(JSON.stringify(request_data, null, "\t")),
			"### Response Data",
			code_block(JSON.stringify(data, null, "\t")),
		].join("\n");
		vhtfm.utils.copy_to_clipboard(traceback_info);
	};

	var show_communication = function () {
		var error_report_message = [
			"<h5>Please type some additional information that could help us reproduce this issue:</h5>",
			'<div style="min-height: 100px; border: 1px solid #bbb; \
				border-radius: 5px; padding: 15px; margin-bottom: 15px;"></div>',
			"<hr>",
			"<h5>App Versions</h5>",
			"<pre>" + JSON.stringify(vhtfm.boot.versions, null, "\t") + "</pre>",
			"<h5>Route</h5>",
			"<pre>" + vhtfm.get_route_str() + "</pre>",
			"<hr>",
			"<h5>Error Report</h5>",
			"<pre>" + exc + "</pre>",
			"<hr>",
			"<h5>Request Data</h5>",
			"<pre>" + JSON.stringify(request_opts, null, "\t") + "</pre>",
			"<hr>",
			"<h5>Response JSON</h5>",
			"<pre>" + JSON.stringify(data, null, "\t") + "</pre>",
		].join("\n");

		var communication_composer = new vhtfm.views.CommunicationComposer({
			subject: "Error Report [" + vhtfm.datetime.nowdate() + "]",
			recipients: error_report_email,
			message: error_report_message,
			doc: {
				doctype: "User",
				name: vhtfm.session.user,
			},
		});
		communication_composer.dialog.$wrapper.css(
			"z-index",
			cint(vhtfm.msg_dialog.$wrapper.css("z-index")) + 1
		);
	};

	if (exc) {
		var error_report_email = vhtfm.boot.error_report_email;

		request_opts = vhtfm.request.cleanup_request_opts(request_opts);

		// window.msg_dialog = vhtfm.msgprint({message:error_message, indicator:'red', big: true});

		if (!vhtfm.error_dialog) {
			vhtfm.error_dialog = new vhtfm.ui.Dialog({
				title: __("Server Error"),
			});

			if (error_report_email) {
				vhtfm.error_dialog.set_primary_action(__("Report"), () => {
					show_communication();
					vhtfm.error_dialog.hide();
				});
			} else {
				vhtfm.error_dialog.set_primary_action(__("Copy error to clipboard"), () => {
					copy_markdown_to_clipboard();
					vhtfm.error_dialog.hide();
				});
			}
			vhtfm.error_dialog.wrapper.classList.add("msgprint-dialog");
		}

		let parts = strip(exc).split("\n");

		let dialog_html = parts[parts.length - 1];

		if (data._exc_source) {
			dialog_html += "<br>";
			dialog_html += `Possible source of error: ${data._exc_source.bold()} `;
		}

		vhtfm.error_dialog.$body.html(dialog_html);
		vhtfm.error_dialog.show();
	}
};

vhtfm.request.cleanup_request_opts = function (request_opts) {
	var doc = (request_opts.args || {}).doc;
	if (doc) {
		doc = JSON.parse(doc);
		$.each(Object.keys(doc), function (i, key) {
			if (key.indexOf("password") !== -1 && doc[key]) {
				// mask the password
				doc[key] = "*****";
			}
		});
		request_opts.args.doc = JSON.stringify(doc);
	}
	return request_opts;
};

vhtfm.request.on_error = function (error_type, handler) {
	vhtfm.request.error_handlers[error_type] = vhtfm.request.error_handlers[error_type] || [];
	vhtfm.request.error_handlers[error_type].push(handler);
};

$(document).ajaxSend(function () {
	vhtfm.request.ajax_count++;
});

$(document).ajaxComplete(function () {
	vhtfm.request.ajax_count--;
	if (!vhtfm.request.ajax_count) {
		$.each(vhtfm.request.waiting_for_ajax || [], function (i, fn) {
			fn();
		});
		vhtfm.request.waiting_for_ajax = [];
	}
});
