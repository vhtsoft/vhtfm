# Copyright (c) 2021, Vhtfm Technologies Pvt. Ltd. and Contributors
# MIT License. See LICENSE

from vhtfm.exceptions import ValidationError


class NewsletterAlreadySentError(ValidationError):
	pass


class NoRecipientFoundError(ValidationError):
	pass


class NewsletterNotSavedError(ValidationError):
	pass
