# coding=utf8
"""mds3

Goes through the config of each requested database and creates the backup,
zipes it, and stores it on s3
"""

__author__		= "Chris Nasr"
__copyright__	= "Ouroboros Coding Inc."
__version__		= "1.1.0"
__email__		= "chris@ouroboroscoding.com"
__created__		= "2023-05-12"

# Limit exports
__all__ = [ 'main' ]

# Python imports
from copy import copy
from datetime import datetime
from json import dumps
from ntpath import basename
from subprocess import run
from time import time

# Pip imports
from jobject import jobject

# Local imports
from .output import error, verbose
from .s3 import put
from .version import __version__

# Constants
MYSQL_DUMP_FIELDS = {
	'host': '-h %s',
	'port': '-P %d',
	'user': '-u %s',
	'password': '-p%s',
	'options': '%s'
}

def mds3(settings: jobject):
	"""MDS3

	Run a mysqldump and load the results onto S3

	Arguments:
		settings (jobject): The configuration for the apps to run

	Returns:
		bool
	"""

	# If we're in verbose mode
	if settings.verbose:
		verbose('Received the following settings:\n%s' % dumps(settings, indent=4))

	# If the bucket is missing
	if 'bucket' not in settings or settings.bucket is None:
		error('"bucket" missing from settings, skipping')
		return False

	# If the key is missing
	if 'key' not in settings or settings.key is None:
		settings.key = 'backup_%Y%m%d%H%M%S.sql'
		if settings.zip:
			settings.key += '.gz'

	# If there's no database, assume the name we are working on
	if 'database' not in settings or settings.database is None:
		error('"database" missing from settings, skipping')
		return False

	# Generate a date time
	dt = datetime.now()

	# Convert possible arguments to the key
	settings.key = dt.strftime(settings.key)

	# Go through each of the possible settings options
	lArgs = []
	for k in MYSQL_DUMP_FIELDS:
		if k in settings:
			lArgs.append(MYSQL_DUMP_FIELDS[k] % settings[k])

	# Get the basename
	file = basename(settings.key)

	# Command
	command = 'mysqldump %(opts)s --databases %(dbs)s%(zip)s' % {
		'dbs': ' '.join(settings.database),
		'file': file,
		'opts': ' '.join(lArgs),
		'zip': ('zip' in settings and settings.zip) and ' | gzip' or ''
	}

	# Run the command to generate the sql data
	result = run(
		command,
		shell=True,
		capture_output=True
	)

	# Add the content to the settings
	settings.content = result.stdout

	# Store the file on S3
	put(settings)

	# Return OK
	return True