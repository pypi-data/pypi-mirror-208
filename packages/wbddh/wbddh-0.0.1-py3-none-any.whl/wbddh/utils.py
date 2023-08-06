import os
import mimetypes
import logging

# try to customize mimetypes as early as possible
if mimetypes.inited:
	logging.warning('mimetypes module has already been initialized. DDH2 is unable to load custom MIME types.')

mimetypes.knownfiles.append(os.path.join(os.path.dirname(__file__), 'ddh.types'))

try:
	import win32clipboard as clipWin
except ImportError:
	clipWin = None
	
try:
	import pasteboard as clipMac
except ImportError:
	clipMac = None



def copy_to_clipboard(text):
	'''Attempt to paste text to the user clipboard

    Arguments:
        text:       text to paste

    Returns:
        True if successful

    '''

	if clipWin:
		clipWin.OpenClipboard()
		clipWin.EmptyClipboard()
		cbid = clipWin.SetClipboardText(text)
		clipWin.CloseClipboard()
		return True
	elif clipMac:
		pb = clipMac.Pasteboard()
		pb.set_contents(text)
		return True

	return False



def _guid(obj):
	'''Guess the guid of the argument

	Arguments:
		obj:		Anything reasonable

	Returns:
		guid
	'''

	if type(obj) is str:
		return obj

	if type(obj) is dict:
		for key in ['dataset_id', 'resource_id', 'id']:
			if key in obj:
				return obj[key]

		raise KeyError('Unrecognized dictionary structure')


	raise ValueError('Unrecognized object type')
