import os
import bibtexparser

from sortedcontainers import SortedListWithKey as slist, SortedSet as sset
from typing import List, Tuple
from functools import reduce

__copyright__ = "Copyright 2017, Léo Flaventin Hauchecorne"
__license__ = "GPLv3"

class Existing(RuntimeError):
	pass


class Store(object):
	"""
	
	"""
	def __init__(self):
		self.l = []
		self.s = []
		self.i = 0
	
	def insert(self, x):
		if self.l:
			i = self.l.pop(0)
			self.s[i] = x
			return i
		else:
			self.s.append(x)
			return len(self.s) - 1
	
	def release(self, ID):
		self.s[ID] = None
		self.l.insert(0, ID)
	
	def replace(self, ID, x):
		
		if self.s[ID] is None:
			self.l.remove(ID)
		self.s[ID] = x
	
	def capacity(self):
		return len(self.s)
	
	def __len__(self):
		return len(self.s) - len(self.l)

	def __getitem__(self, k):
		return self.s[k]

	def values(self):
		return (s for s in self.s if s is not None)

	def container(self):
		return self.s
	
	def __iter__(self):
		return iter(enumerate(self.s))

	def idMax(self):
		i = -1
		s = self.s
		m = -len(s) - 1
		while s[i] is None:
			i-=1
			if i is m:
				return None
		return len(s) + i
	
	def reserve(self, nb):
		s = self.s
		curS = len(s)
		if nb <= curS:
			return
		s.extend([None] * (nb-curS))
		self.l.extend(list(range(curS, nb)))
		
		

class StoreWithName(Store):
	def __init__(self):
		super().__init__()
		self.byName = {}
	
	def insert(self, x):
		self.byName[x.name] = x
		return super().insert(x)

	def replace(self, ID, x):
		old = self[ID]
		if old is None:
			self.byName[x.name] = x
		elif old.name != x.name:
			del self.byName[old.name]
			self.byName[x.name] = x
		return super().replace(ID, x)
	
	def release(self, ID):
		x = self[ID]
		del self.byName[x.name]
		return super().release(ID)
	
	def __len__(self):
		return len(self.byName)
	
	def fromName(self, n):
		return self.byName[n]

class Entry(object):
	def __init__(self, name : str, bibtex : dict, tags : List[str], priority : float, depends : None, url = '', comment=''):
		self.name = name
		self.ID = None
		self.bibtex = bibtex
		self.comment = comment
		self.url = url
		self.tags = tags
		self.priority = priority
		self.depends = depends
		self._location = None
		
	def path(self):
		if self._location:
			return self._location.path()
		return []
	
	def pathstr(self):
		if self._location:
			return '/' + self._location.pathstr()
		return ''
	
	def fullpathstr(self):
		if self._location:
			s = self._location.pathstr()
			if s == '':
				return '/' + self.name
			else:
				return '/' + s + '/' + self.name
		return ''
	
	def toDict(self):
		return {'ID' : self.ID, 'comment' : self.comment, 'tags': self.tags, 'priority' : self.priority, 'depends': self.depends, 'path' : self.path() }
	
	@staticmethod
	def fromDict(d):
		t = Entry(d['content'], d['tags'], d['priority'], d['depends'])
		t.ID = d['ID']
		return t


_priorityFn = lambda x: x.priority
_path_priorityFn = lambda x: (x.pathstr(), x.priority)



class EntryRepo(object):
	"""
	
	"""
	def __init__(self, name = '', parent = None):
		self.children = {}
		self.parent = parent
		self.entries = slist(key=_priorityFn)
		self.name = name
		self._pathChanged = True
		self._path = []
		self._pathstr = []
	
	def add(self, t):
		self.entries.add(t)
		t._location = self
	
	def rem(self, t):
		self.entries.remove(t)
	
	def clear(self):
		self.children = {}
		self.entries = slist(key=_priorityFn)
	
	def _updatePath(self):
		if self.parent is None:
			self._path = []
		else:
			self._path = self.parent.path() + [self.name]
		self._pathstr = '/'.join(self._path)
		self._pathChanged = False
	
	def path(self):
		if self._pathChanged :
			self._updatePath()
		return self._path
	
	def pathstr(self):
		if self._pathChanged :
			self._updatePath()
		return self._pathstr
	
	def __getitem__(self, k):
		if not isinstance(k, str):
			return reduce(lambda x, y: x[y], k, self)
		if k == '':
			return self
		v = self.children.get(k)
		if v is None:
			v = EntryRepo(k, self)
			self.children[k] = v
		return v
	
	@staticmethod
	def p_br(p, l):
		return l.bisect_key_right(p)
	
	@staticmethod
	def p_bl(p, l):
		return l.bisect_key_left(p)
	
	@staticmethod
	def noMin(l):
		return None
	
	@staticmethod
	def noMax(l):
		return None
	
	def filter_legacy(self, tags, minFn, maxFn, pattern):
		entries = self.entries
		match = pattern.fullmatch if pattern else lambda x: True
		yield from ( t for t in entries[minFn(entries):maxFn(entries)] if all(tag in t.tags for tag in tags) and match(t.pathstr()) )
		for v in self.children.values():
			yield from v.filter_legacy(tags, minFn, maxFn, pattern)



class TagRepo(object):
	"""
	
	"""
	def __init__(self):
		self.tags = {}
	
	def __getitem__(self, k):
		v = self.tags.get(k)
		if v is None:
			v = slist(key=path_priorityFn)
			self.tags[k] = v
		return v
	
	def rem(self, entry):
		for t in entry.tags:
			self.tags[t].remove(entry)
	
	def add(self, entry):
		for t in entry.tags:
			tl = self.tags.get(t)
			if tl is None:
				self.tags[t] = slist((entry,), key=_priorityFn)
			else:
				tl.add(entry)
	
	def clear(self):
		self.tags = {}


class Torefl(object):
	"""
	
	"""
	def __init__(self, location=os.getcwd()):
		self.location = location
		self.store = StoreWithName()
		self.root = EntryRepo()
		self.tags = TagRepo()
		self.entries = slist(key=lambda x:(x.location(), x.priority))
	
	def reserve(self, nb):
		self.store.reserve(nb)
	
	def add(self, entry, path):
		entry.ID = self.store.insert(entry)
		self.root[path].add(entry)
		self.tags.add(entry)
	
	def place(self, ID, entry, path):
		if self.store[ID] is not None:
			raise ValueError('ID '+ID+' already taken')
		entry.ID = ID
		self.store.replace(ID, entry)
		self.root[path].add(entry)
		self.tags.add(entry)
	
	def update(self, entry, newEntry):
		newEntry.ID = entry.ID
		self.store.replace(entry.ID, newEntry)
		rep = self.root[entry.path()]
		rep.rem(entry)
		rep.add(newEntry)
		self.tags.rem(entry)
		self.tags.add(newEntry)

