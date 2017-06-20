import argparse

from torefl.core import *
import torefl.shell as shell

__copyright__ = "Copyright 2017, Léo Flaventin Hauchecorne"
__license__ = "GPLv3"

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-q', action='store_true', help='Write cache and quit')
	parser.set_defaults(func=shell._default, file='biblio')
	sub = parser.add_subparsers(title='Action', description='Valid sub commands :')
	p_create = sub.add_parser('create', aliases=['c'], help='Create a bib tree')
	p_create.add_argument('file', action='store', nargs='?', default='biblio', help='Name of the database file to create (without extension)')
	p_create.set_defaults(func=shell._create)
	p_update = sub.add_parser('update', aliases=['u'], help='Update a bib tree')
	p_update.add_argument('file', action='store', nargs='?', default='biblio', help='Name of the database to use/update')
	p_update.set_defaults(Action=p_update)
	args = parser.parse_args()
	path, r = args.func(args)
	if not args.q:
		sh = shell.Shell()
		sh.path = path
		sh.registers = r
		sh.cmdloop()

