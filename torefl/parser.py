
import re
import bibtexparser
from torefl import Entry


__copyright__ = "Copyright 2017, Léo Flaventin Hauchecorne"
__license__ = "GPLv3"


def iterStrip(l):
	return iter(s.strip() for s in l)

def cap(s):
	return s[0].upper() + s[1:]

def formatTag(tag):
	l = tag.split('_')
	return ''.join(cap(s) for s in l)


class Collector(object):
	"""
	
	"""
	def __init__(self):
		self.l = []
	
	def __call__(self, match):
		self.l.append(self.parse(match))
		return ''

	def sub(self, s):
		return self.regex.sub(self, s)


class TagCollector(Collector):
	regex = re.compile(r'(?:^|\s)\#(\w+)')
	def parse(self, m):
		return formatTag(m[1])

class PriorityCollector(Collector):
	regex = re.compile(r'(?:^|\s)@((\d+\.\d+)|(\d+))')
	def parse(self, m):
		return float(m[1])

id_re = re.compile(r'(?:^|\s)&(\d+)')
ide_re = re.compile(r'(?:^|\s)&(\w+)')
path_re = re.compile(r'(/\w+)+|/')
path_f_re = re.compile(r'(/(\w|\*)+)+|/')
priority_f_re = re.compile(r'(?:^|\s)@(?P<cmp>(<=|>=|<|>)?)(?P<p>(\d+\.\d+)|(\d+))')

def parseComment(comment):
	tc = TagCollector()
	pc = PriorityCollector()
	comment = "".join( pc.sub(tc.sub(s)) for s in comment ).strip()
	return comment, tc.l, pc.l[0] if pc.l else float(0)

def parseEntry(f, name, pdf_path):
	lines = iter(f)
	comment = []
	bibtex = []
	for li in lines:
		if li.startswith('****************'):
			break
		comment.append(li)
	for li in lines:
		bibtex.append(li)
	return createEntry(name, pdf_path, comment, bibtex)

def createEntry(name, pdf_path, comment, bibtex):
	bib = ''.join(bibtex)
	#Todo Catch exceptions
	try:
		db = bibtexparser.loads(bib)
		if db.entries:
			parsedBib = db.entries[0]
		else:
			print(F.RED, 'No citation for ', name, F.RESET, sep='')
			parsedBib = None
	except Exception as e:
		print('EX :', e.__class__.__name__)
		print(e)
		parsedBib = None
	comment, tag_list, priority = parseComment(comment)
	return Entry(name, parsedBib, tag_list, priority, None, url=pdf_path, comment=comment)

class UnsupportedVersion(RuntimeError):
	pass

base000_line_re = re.compile(r'(?P<ID>\d+):(?P<name>.+):(?P<title>.*)')
base000_register_re = re.compile(r'(?P<ID>[^:]+):(?P<sel>(\d+(\s+\d+)*)?)')

def parseBase000(it):
	nb = int(next(it))
	e = []
	for l in it:
		l = l.strip()
		if l.startswith('****************'):
			break
		t = base000_line_re.fullmatch(l)
		if t:
			e.append(t)
	r = []
	for l in it:
		l = l.strip()
		t = base000_register_re.fullmatch(l)
		if t:
			r.append(t)
	return	(
						{ m.group('name') : int(m.group('ID')) for m in e if m },
						{ m.group('title') : int(m.group('ID')) for m in e if m and m.group('title') != '' },
						nb,
						( (m.group('ID'), map(int, m.group('sel').split())) for m in r ),
					)

def parseBase(f):
	it = iterStrip(f)
	v = next(it)
	if v == '_torefl000':
		return parseBase000(it)
	else:
		raise UnsupportedVersion(v)
		

