import vhtfm


class MaxFileSizeReachedError(vhtfm.ValidationError):
	pass


class FolderNotEmpty(vhtfm.ValidationError):
	pass


class FileTypeNotAllowed(vhtfm.ValidationError):
	pass


from vhtfm.exceptions import *
