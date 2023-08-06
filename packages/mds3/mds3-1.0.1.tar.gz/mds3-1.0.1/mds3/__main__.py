# coding=utf8
""" CLI

Used for shim to run the program from the command line
"""

__author__		= "Chris Nasr"
__copyright__	= "Ouroboros Coding Inc."
__version__		= "1.0.0"
__email__		= "chris@ouroboroscoding.com"
__created__		= "2023-05-12"

# Limit exports
__all__ = [ 'cli' ]

# Python imports
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from os import path
from configparser import ConfigParser
import sys

# Pip imports
from jobject import jobject

# Local imports
from . import info, mds3, version
from .output import color, error

def cli():
	"""CLI

	Called from the command line to load a config file and run mds3

	Returns:
		uint
	"""

	# Setup the argument parser
	parser = ArgumentParser(
		formatter_class=RawDescriptionHelpFormatter,
		description=info.description,
		epilog=info.epilog
	)

	# Say hello
	color('light_magenta', '%s v%s' % (info.description, version.__version__))

	# Add the cli only arguments
	parser.add_argument('sections', metavar='N', type=str, nargs='*', help=info.cli.sections.help)
	parser.add_argument('-c', '--config', help=info.cli.config.help)

	# Add all the info arguments
	for arg in info.settings:
		o = info.settings[arg]
		if 'action' in o and o.action in ['store_true', 'store_false']:
			parser.add_argument(
				'-%s' % o.short,
				'--%s' % arg,
				action=o.action,
				help=o.help
			)
		else:
			parser.add_argument(
				'-%s' % o.short,
				'--%s' % arg,
				action=('action' in o and o.action or 'store'),
				type=('type' in o and o.type or str),
				nargs=('nargs' in o and o.nargs or 1),
				help=o.help
			)

	# Parse the arguments
	args = parser.parse_args()

	# If the config was not set
	if not args.config:
		args.config = '~/.mds3'

	# Expand the path if necessary
	args.config = path.expanduser(args.config)

	# Attempt to load the config file
	try:
		cp = ConfigParser(interpolation=None)
		cp.read(args.config)
		cp.add_section('_NO_SECTION_')
		config = {}

		# Go through each available section
		for s in cp.sections():
			v = {}

			# Go through the possible settings
			for k in info.settings:

				# Get the default value
				try: default = info.settings[k].default
				except AttributeError: default = None

				# Get the function
				try: func = info.settings[k].get_func
				except AttributeError: func = 'get'

				# Fetch the data from the config
				v[k] = getattr(cp[s], func)(k, default)

				# If it's the database
				if k == 'database' and v[k]:
					v[k] = v[k].split(' ')

			# Store the values in the config
			config[s] = v

	except IOError as e:
		config = {}

	# Turn it into a jobject
	config = jobject(config)

	# If we have no sections
	if not args.sections:
		args.sections = ['_NO_SECTION_']

	# Init the return as success (0 is success for program return)
	iRet = 0

	# Go through each section provided
	for s in args.sections:

		# Init the settings using the defaults as a starting point
		try:
			settings = jobject(config[s])
		except KeyError:
			error('can not find section "%s", skipping' % s)
			continue

		# Step through the arguments
		for k in info.settings:
			if k in args.__dict__ and args.__dict__[k]:
				settings[k] = args.__dict__[k]

		# Call the mds3 method with the settings we've gathered
		if not mds3(settings):
			iRet = 1

	# Return if any of the sections failed or not
	return iRet

# Only run if main
if __name__ == '__main__':
	sys.exit(
		cli()
	)