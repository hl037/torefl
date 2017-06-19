
def getAll(r, arg):
	res = []
	m = r.search(arg)
	while m:
		res.append(m)
		arg = arg[:m.start()].strip() + arg[m.end():]
		m = r.search(arg)
	return res, arg

def getRepoPath(x):
	i = x.find('*')
	if i == -1:
		pre = x.split('/')
		del pre[0]
		return root[pre], None
	else:
		pre = x[:i].split('/')
		del pre[0]
		del pre[-1]
		return root[pre], re.compile(fnmatch.translate(x))

