import appdirs
import configparser
import os.path
from collections import OrderedDict

__copyright__ = "Copyright 2007, Léo Flaventin Hauchecorne"
__license__ = "GPLv3"

_dirs = appdirs.AppDirs('torefl', 'hl037')

_defaults = {
		'edit_cmd' : 'vim "$f"',
		'edit_same_win' : '1',
		'open_cmd' : 'okular "$f"',
		'open_same_win' : '0',
}

_initial = OrderedDict((
		('DEFAULT', _defaults),
		('Torefl', _defaults),
		))

conf = configparser.ConfigParser()

conf.read_dict(_initial)

def write():
	with open(os.path.join(_dirs.user_config_dir, 'torefl.ini'), 'w') as f:
		conf.write(f)

if not os.path.isdir(_dirs.user_config_dir):
	os.makedirs(_dirs.user_config_dir)

try:
	with open(os.path.join(_dirs.user_config_dir, 'torefl.ini'), 'r') as f:
		conf.read_file(f, 'torefl.ini')
except:
	write()


	


