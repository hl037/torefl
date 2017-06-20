
import bibtexparser
import copy

from torefl import Entry
from typing import Iterable

__copyright__ = "Copyright 2017, Léo Flaventin Hauchecorne"
__license__ = "GPLv3"

def _getBib(e:Entry):
	b = copy.deepcopy(e.bibtex)
	b['ID'] = e.name
	return b	

def export(f, entries:Iterable[Entry] ):
	db = bibtexparser.bibdatabase.BibDatabase()
	db.entries = [ _getBib(e) for e in entries if e.bibtex is not None ]
	bibtexparser.dump(db, f)




