
from colorama import Fore as _F, Back as _B, Style as _S, init as _colorama_init
from torefl.core import Entry

__copyright__ = "Copyright 2007, Léo Flaventin Hauchecorne"
__license__ = "GPLv3"

def formatEntry(e:Entry):
	R = _S.RESET_ALL
	ID = R + _B.BLUE
	P = R + _F.LIGHTGREEN_EX
	TAG = R + _F.RED
	NAME = R + _B.RED
	Bd = R + _F.CYAN
	PATH = R + _F.YELLOW
	TITLE = R + _F.LIGHTMAGENTA_EX
	AUTHORS = R + _F.MAGENTA
	prefix = Bd + '|  ' + R
	comment = ( s + '\n' + prefix for s in e.comment.split('\n') ) if e.comment != '' else ()
	
	return ''.join( (
		Bd, '--------------------------------------------------------------------------------', R, '\n',
		prefix, ID, 'ID : ', '{:>5}'.format(e.ID or ''), R, ' '*47, P, '{:>20}'.format(e.priority), R, '\n',
		prefix, NAME, e.name, R, '\n',
		prefix, PATH, e.pathstr(), R, '\n',
		*( (
			prefix, TITLE, e.bibtex.get('title', ''), R, '\n',
			prefix, AUTHORS, e.bibtex.get('author', ''), R, '\n',
			) if e.bibtex else (
			prefix, TITLE, '<No Bibtex>', R, '\n')
		),
		prefix, (R + ' ').join(''.join((TAG, '#', t)) for t in e.tags), '\n', 
		prefix, R, *comment , '\n',
		Bd, '--------------------------------------------------------------------------------', R, '\n',
		))

