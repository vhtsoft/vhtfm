vhtfm.route_history_queue = [];
const routes_to_skip = ["Form", "social", "setup-wizard", "recorder"];

const save_routes = vhtfm.utils.debounce(() => {
	if (vhtfm.session.user === "Guest") return;
	const routes = vhtfm.route_history_queue;
	if (!routes.length) return;

	vhtfm.route_history_queue = [];

	vhtfm
		.xcall("vhtfm.desk.doctype.route_history.route_history.deferred_insert", {
			routes: routes,
		})
		.catch(() => {
			vhtfm.route_history_queue.concat(routes);
		});
}, 10000);

vhtfm.router.on("change", () => {
	const route = vhtfm.get_route();
	if (is_route_useful(route)) {
		vhtfm.route_history_queue.push({
			creation: vhtfm.datetime.now_datetime(),
			route: vhtfm.get_route_str(),
		});

		save_routes();
	}
});

function is_route_useful(route) {
	if (!route[1]) {
		return false;
	} else if ((route[0] === "List" && !route[2]) || routes_to_skip.includes(route[0])) {
		return false;
	} else {
		return true;
	}
}
