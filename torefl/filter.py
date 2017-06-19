
import re
import fnmatch
import operator

from typing import List, Tuple
from torefl.parser import *
from torefl.core import Entry

__copyright__ = "Copyright 2007, Léo Flaventin Hauchecorne"
__license__ = "GPLv3"

class BibFilter(object):
	__slots__ = ('checkList')
	def __init__(self, checkList : List[Tuple[str, str]]):
		self.checkList = checkList
	
	def __call__(self, entry : Entry):
		if entry.bibtex is None:
			return False
		b = entry.bibtex
		try:
			if not all((v not in b[k[1:]].lower()) if k[0] == '!' else (v in b[k].lower()) for k, v in self.checkList):
				return False
		except KeyError:
			return False
		else:
			return True

class BibFilterHandler(object):
	def __init__(self):
		self.tokens = []
	
	def __call__(self, tok : str):
		self.tokens.append(tok.lower())
	
	def get(self):
		l = self.tokens
		return BibFilter([(l[i], l[i+1]) for i in range(0, len(l), 2)])

class CommentFilter(object):
	__slots__ = ('checks')
	def __init__(self, checks : List[str]):
		self.checks = checks
	
	def __call__(self, entry : Entry):
		c = entry.comment.lower()
		return all(s in c for s in self.checks)

class PathFilter(object):
	__slots__ = ('re',)
	def __init__(self, path):
		self.re = re.compile(fnmatch.translate(path))
	def __call__(self, entry: Entry):
		return bool(self.re.fullmatch(entry.pathstr()))

class TagFilter(object):
	__slots__ = ('tag',)
	def __init__(self, tag):
		self.tag = formatTag(tag)
	def __call__(self, entry : Entry):
		return self.tag in entry.tags

class PriorityFilter(object):
	__slots__ = ('fun', 'p')
	def __init__(self, p_match):
		c = p_match['cmp']
		if   c == '>=':
			self.fun = operator.ge
		elif c == '>':
			self.fun = operator.gt
		elif c == '<=':
			self.fun = operator.le
		elif c == '<':
			self.fun = operator.lt
		else:
			self.fun = operator.eq
		self.p = float(p_match['p'])
	def __call__(self, entry: Entry):
		return self.fun(entry.priority, self.p)

class AndFilter(object):
	__slots__ = ('filters')
	def __init__(self, filters):
		self.filters = filters
	def __call__(self, entry : Entry):
		return all(f(entry) for f in self.filters)

class NotFilter(object):
	__slots__ = ('filter')
	def __init__(self, filter):
		self.filter = filter
	def __call__(self, entry : Entry):
		return not self.filter(entry)

identity = lambda x : x
not_op = lambda x : NotFilter(x)
	

def LegacyFilter(tokens):
	filters = []
	for t in tokens:
		if t[0] == '!':
			f = not_op
			t = t[1:]
		else:
			f = identity
		m = path_f_re.fullmatch(t)
		if m:
			filters.append(f(PathFilter(m[0])))
			continue
		m = TagCollector.regex.fullmatch(t)
		if m:
			filters.append(f(TagFilter(m[1])))
			continue
		m = priority_f_re.fullmatch(t)
		if m:
			filters.append(f(PriorityFilter(m)))
			continue
	return AndFilter(filters)

class GenericFilterHandler(object):
	__slots__ = ('tokens','Filter','lower')
	def __init__(self, Filter, lower = True):
		self.tokens = []
		self.Filter = Filter
		self.lower = lower
		
	def __call__(self, tok : str):
		self.tokens.append(tok.lower() if self.lower else tok)
	
	def get(self):
		return self.Filter(self.tokens)


filterHandlers = {
		'bib' : BibFilterHandler,
		'com' : lambda : GenericFilterHandler(CommentFilter),
		'leg' : lambda : GenericFilterHandler(LegacyFilter, False),
}


def getFilterFunctions(args):
	h = filterHandlers['leg']()
	r = []
	for a in args:
		if a[0] == '-':
			r.append(h.get())
			h = filterHandlers[a[1:]]()
		else:
			h(a)
	r.append(h.get())
	return r

