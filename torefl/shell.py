
import operator
import sys
import cmd
import os
import sys
from functools import partial
from itertools import chain
import json
import bibtexparser
import shlex
import traceback
import subprocess
from typing import List, Tuple

from colorama import Fore as _F, Back as _B, Style as _S, init as _colorama_init
from torefl.formatters import ASCIIFormatter as _ASCIIFormatter
from torefl import Torefl, Entry
from torefl.filter import getFilterFunctions
from torefl.exporters import BibtexExporter
from torefl.config import conf, write as writeConf
from torefl.parser import parseEntry, parseBase

__copyright__ = "Copyright 2017, Léo Flaventin Hauchecorne"
__license__ = "GPLv3"

class _listHack(list):
	"""
	
	"""
	def __init__(self, g):
		self.g = g
	
	def __iter__(self):
		return iter(self.g)
	
	def __len__(self):
		return len(self.g)

	def __getitem__(self, k):
		return self.g[k]

_torefl = Torefl()

_store = _torefl.store
_root = _torefl.root
_tags = _torefl.tags
_entries = _torefl.entries


def _updateGlobal():
	global _store
	global _root
	global _tags
	global _entries
	_store = _torefl.store
	_root = _torefl.root
	_tags = _torefl.tags
	_entries = _torefl.entries

_updateGlobal()

def _GetOrInsert(defaultClass):
	def f(d, key):
		try:
			return d[key]
		except KeyError:
			r = defaultClass()
			d[key] = r
			return r
	return f

_getOrInsertSet = _GetOrInsert(set)

def _getById(torefl:Torefl, id) -> Entry:
	try:
		return torefl.store[int(id)]
	except:
		return torefl.store.fromName(id)

def _getPath(torefl:Torefl, e:Entry, ext:str):
	return os.path.join(torefl.location, e.pathstr()[1:], e.name + ext)

def _exec(line:str, same_win:bool):
	argv = shlex.split(line)
	if same_win:
		subprocess.run(argv)
	else:
		subprocess.Popen(argv, stdout = subprocess.DEVNULL)

class Shell(cmd.Cmd):
	intro = 'torefl shell'
	prompt = 'torefl / >'

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.selection = set()
		self.registers = {}
	
	@staticmethod
	def parse(arg):
		res = {}
		i = 0
		m = path_re.match(arg, i)
		if m:
			res['path'] = m[0][1:].split('/')
			arg = arg[m.end():].strip()
		else:
			res['path'] = []
			
		l = []
		m_tag, arg = getAll(TagCollector.regex, arg)
		res['tags'] = [ formatTag(m[1]) for m in m_tag ]
		
		m = PriorityCollector.regex.search(arg)
		if m:
			res['priority'] = float(m[1])
			arg = (arg[:m.start()] + arg[m.end():]).strip()
		else:
			res['priority'] = 0.
		res['_'] = arg
		return res
		
	def Rem(self, arg):
		for ID in map(int, arg.split()):
			try:
				t = _store[ID]
			except:
				print(_F.RED, 'ID %s Not found' % ID, _S.RESET_ALL, sep='')
			else:
				r = _root[t.path()[1:]]
				r.rem(t)
				_tags.rem(t)
				_store.release(ID)
				print(_F.BLUE, 'Entry removed : \n', str(t), sep='')
	
	def LegacyFilter(self, arg):
		m_path, arg = getAll(path_f_re, arg)
		if m_path:
			paths = [m[0] for m in m_path]
		else:
			paths = ['/']
		
		m_tag, arg = getAll(TagCollector.regex, arg)
		_tags = [ formatTag(m[1]) for m in m_tag ]
			
		m_priority, arg = getAll(priority_f_re, arg)
		minFn = EntryRepo.noMin
		maxFn = EntryRepo.noMax
		for m in m_priority:
			p = float(m['p'])
			c = m['cmp']
			if   c == '>=':
				minFn = partial(EntryRepo.p_bl, p)
			elif c == '>':
				minFn = partial(EntryRepo.p_br, p)
			elif c == '<=':
				maxFn = partial(EntryRepo.p_br, p)
			elif c == '<':
				maxFn = partial(EntryRepo.p_bl, p)
			else:
				minFn = partial(EntryRepo.p_bl, p)
				maxFn = partial(EntryRepo.p_br, p)
		return sset( chain.from_iterable( repo.filter_legacy(_tags, minFn, maxFn, pattern) for repo, pattern in (getRepoPath(x) for x in paths) ), key = lambda x: (x.pathstr(), x.priority, x.ID) )

	def Filter(self, args):
		lf = getFilterFunctions(args[1:])
		return [ e for e in _torefl.store.values() if all(f(e) for f in lf) ]
		

	def load(self, st):
		_tags.clear()
		_root.clear()
		o = json.load(st)
		_store.i = o['maxSize']
		print('maxSize : ', o['maxSize'])
		s = [None] * _store.i
		_store.s = s
		for t in o['entries']:
			print('ID : ', repr(t['ID']))
			ta = Entry.fromDict(t)
			s[t['ID']] = ta
			_tags.add(ta)
			_root[t['path']].add(ta)
		print(s)
		_store.l = [i for i, v in _store]
			
	def open(self, path):
		with open(path, 'r', encoding='utf-8') as f:
			self.load(f)
	
	def Load(self, arg):
		if arg:
			self.path = arg
		self.open(self.path, encoding='utf-8')
	
	def save(self, path):
		with open(path, 'w', encoding='utf-8') as st:
			_writeTorefl(st, _torefl, self.registers)
		

	def Save(self, arg):
		self.save(self.path if len(arg) == 0 else arg[1])
	
	def Quit(self, arg):
		if arg == '!':
			return True
		if arg:
			self.path = arg
		self.save(self.path)
		return True
	
	def List(self, arg):
		l = self.Filter(arg) 
		self.selection = set(l)
		for t in l :
			print(_ASCIIFormatter.formatEntry(t))
			
	def Sel(self, arg):
		if arg[0] in ('&=', '^=', '|=', '-=', '='):
			c = [ None, arg[0], arg[1] if len(arg) is 2 else None ]
		else:
			c = [ arg[0], arg[1], arg[2] if len(arg) is 3 else None ]
		if c[0] is None:
			s0 = self.selection
		else:
			s0 = _getOrInsertSet(self.registers, c[0])
		if c[2] is None:
			s1 = self.selection
		elif c[2] == '0':
			s1 = set()
		else:
			s1 = _getOrInsertSet(self.registers, c[2])
		if c[1] == '=':
			s0.clear()
			s0 |= s1
		else:
			exec('s0 ' + c[1] + 's1')
		
	def ListSel(self, arg):
		if len(arg) is 0:
			s = self.selection
		else:
			s = self.registers[arg[0]]
		for t in s:
			print(_ASCIIFormatter.formatEntry(t))
	
	def Export(self, arg):
		if arg[0] == 'bib':
			with open(arg[1], 'w', encoding='utf-8') as f:
				BibtexExporter.export(f, self.registers[arg[2]] if len(arg) > 2 else self.selection)
		else:
			print('Unknown exporter', arg[0])
	
	def Edit(self, arg):
		e = _getById(_torefl, arg[0])
		f = _getPath(_torefl, e, EXT)
		c = conf['Torefl'].get('edit_cmd')
		c = c.replace('$f', f)
		same_win = conf['Torefl'].getboolean('edit_same_win')
		_exec(c, same_win)
		with open(f, 'r') as f:
			n = parseEntry(f, e.name, e.url)
		_torefl.update(e, n)
		
	def Open(self, arg):
		e = _getById(_torefl, arg[0])
		f = _getPath(_torefl, e, '.pdf')
		c = conf['Torefl'].get('open_cmd')
		c = c.replace('$f', f)
		same_win = conf['Torefl'].getboolean('open_same_win')
		_exec(c, same_win)
	
	def default(self, line):
		argv = shlex.split(line)
		if argv[0] in ('l', 'list'):
			return self.List(argv)
		if argv[0] in ('s', 'sel', 'selection'):
			return self.Sel(argv[1:])
		if argv[0] in ('ls',):
			return self.ListSel(argv[1:])
		if argv[0] in ('e', 'export'):
			return self.Export(argv[1:])
		if argv[0] in ('ed', 'edit'):
			return self.Edit(argv[1:])
		if argv[0] in ('o', 'open'):
			return self.Open(argv[1:])
		
	def emptyline(self):
		pass

	def onecmd(self, s):
		try:
			return super().onecmd(s)
		except:
			traceback.print_exc()
	
	
	#do_a = Add
	#do_add = Add
	
	#do_r = Rem
	#do_rem = Rem
	#do_remove = Rem
	
	do_save = Save
	do_sa = Save
	
	#do_o = Load
	#do_open = Load
	
	do_q = Quit
	do_quit = Quit



EXT = '.torefl'
EXT_BASE = '.toreflbase'

def _writeTorefl(st, _torefl, regs):
	store = _torefl.store
	st.write('_torefl000\n')
	st.write(str(len(store))+ '\n')
	st.write(' '.join(str(i) for i in store.l ))
	for v in store.values() :
		if v is not None:
			st.write(str(v.ID) + ':' + v.name + ':' + (v.bibtex.get('title', '') if v.bibtex else '') + '\n')
	st.write('****************\n')
	for k, v in regs.items():
		st.write(k + ':' + ' '.join(str(e.ID) for e in v) + '\n')

def _writeCache(st, torefl):
	pass


def walkTorefl(p):
	ext_len = len(EXT)
	l = [p]
	current = []
	for _current, dirs, files in os.walk(p):
		rel = os.path.relpath(_current, p)
		if rel == '.':
			current = []
		else:
			current = rel.split(os.sep)
		for f in files:
			if f.endswith('.torefl'):
				name = f[:-len(EXT)]
				pdf_path = current+[name+'.pdf']
				if not os.path.exists(os.sep.join(pdf_path)):
					pdf_path = None
				with open(os.sep.join(current + [f]), encoding='utf-8') as bib:
					e = parseEntry(bib, name, pdf_path)
					yield e, current
		l.append(None)


def _create(args):
	global _torefl
	_torefl = Torefl()
	_updateGlobal()
	for e, path in walkTorefl(os.getcwd()):
		_torefl.add(e, path)
	o = args.file + EXT_BASE
	with open(o, 'w', encoding='utf-8') as of:
		_writeTorefl(of, _torefl, {})
	#with open('.'+o+'.cache', 'w', encoding='utf-8') as of:
	#	_writeCache(of, _torefl)
	return o, []

def _update(args):
	global _torefl
	_torefl = Torefl()
	_updateGlobal()
	o = args.file + EXT_BASE
	with open(o, 'r', encoding='utf-8') as f:
		d1, d2, n, r = parseBase(f)
	#print('R', [ (n, list(m)) for n, m in r])
	_torefl.reserve(n)
	l = []
	for e, path in walkTorefl(os.getcwd()):
		try:
			ID = d2[e.bibtex['title']]
		except:
			ID = d1.get(e.name, None)
		if ID is not None:
			_torefl.place(ID, e, path)
		else:
			l.append((e, path))
	for e, path in l:
		_torefl.add(e, path)
	r = { k : { _store[ID] for ID in v if _store[ID] is not None } for k, v in r }
	with open(o, 'w', encoding='utf-8') as of:
		_writeTorefl(of, _torefl, r)
	#with open('.'+o+'.cache', 'w', encoding='utf-8') as of:
	#	_writeCache(of, _torefl)
	return o, r

def _default(args):
	o = args.file + EXT_BASE
	if os.path.isfile(o):
		return _update(args)
	else:
		return _create(args)

	
