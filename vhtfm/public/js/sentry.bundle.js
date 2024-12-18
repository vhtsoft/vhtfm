import * as Sentry from "@sentry/browser";

Sentry.init({
	dsn: vhtfm.boot.sentry_dsn,
	release: vhtfm?.boot?.versions?.vhtfm,
	autoSessionTracking: false,
	initialScope: {
		// don't use vhtfm.session.user, it's set much later and will fail because of async loading
		user: { id: vhtfm.boot.sitename },
		tags: { vhtfm_user: vhtfm.boot.user.name ?? "Unidentified" },
	},
	beforeSend(event, hint) {
		// Check if it was caused by vhtfm.throw()
		if (
			hint.originalException instanceof Error &&
			hint.originalException.stack &&
			hint.originalException.stack.includes("vhtfm.throw")
		) {
			return null;
		}
		return event;
	},
});
