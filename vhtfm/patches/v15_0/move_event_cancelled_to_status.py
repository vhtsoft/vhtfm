import vhtfm


def execute():
	Event = vhtfm.qb.DocType("Event")
	query = (
		vhtfm.qb.update(Event)
		.set(Event.event_type, "Private")
		.set(Event.status, "Cancelled")
		.where(Event.event_type == "Cancelled")
	)
	query.run()
