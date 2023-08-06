# coding=utf8
""" Arguments

Provides strings for describing help as well as default values
"""

# Pip imports
from jobject import jobject

description	= 'MySQL Dump to S3'

settings = jobject({
	'bucket': {
		'short': 'b',
		'help': 'The AWS S3 bucket to put the backup on',
	},
	'database': {
		'short': 'd',
		'help': 'The name(s) of the database(s) to dump',
		'nargs': '+'
	},
	'host': {
		'short': 'H',
		'default': 'localhost',
		'help': 'The hostname of the MySQL/MariaDB server (default localhost)',
	},
	'key': {
		'short': 'k',
		'default': 'backup_%Y%m%d%H%M%S.sql',
		'help': 'The name of the key to use to store the file on S3 (default backup_%%Y%%m%%d%%H%%M%%S.sql[.gz])',
	},
	'options': {
		'short': 'o',
		'default': '--triggers --routines --events --lock-tables',
		'help': 'Additional options to pass to mysqldump, must be passed as a quoted string. %(prog)s -o "--events --lock-tables" (default "--triggers --routines --events --lock-tables")'
	},
	'password': {
		'short': 'p',
		'help': 'The password used to connect to the MySQL/MariaDB server',
	},
	'port': {
		'short': 'P',
		'default': 3306,
		'help': 'The port of the MySQL/MariaDB server (default 3306)',
		'get_func': 'getint'
	},
	'profile': {
		'short': 'pr',
		'default': 'mds3',
		'help': 'The profile, found in ~/.aws/config, used to connect to AWS S3 (default mds3)',
	},
	'user': {
		'short': 'u',
		'help': 'The user used to connect to the MySQL/MariaDB server',
	},
	'verbose': {
		'short': 'v',
		'default': False,
		'help': 'Set to display more information when backing up the database(s)',
		'action': 'store_true',
		'get_func': 'getboolean'
	},
	'zip': {
		'short': 'z',
		'default': False,
		'help': 'Use to compress (gzip) the data before storing',
		'action': 'store_true',
		'get_func': 'getboolean'
	}
})

cli = jobject({
	'config': {
		'help': 'The configuration file to load (default ~/.mds3)'
	},
	'sections': {
		'help': 'One or more sections in the config file to run instead of setting arguments individually. e.g. %(prog)s primary'
	}
})

epilog = \
"""----------------------------------------
Key Formatting

Keys can be formatted using python's datetime formatting. More information can
be found at:

https://docs.python.org/3.10/library/datetime.html#strftime-strptime-behavior

----------------------------------------
Configuration File

By using the MDS3 configuration file, normally found in ~/.mds3, we can cut
out a lot of the repetitive work of making backups.

For example, we could make sure that every backup run is zipped by default, by
setting our configuration file to

$: echo '[DEFAULT]
zip = true
' > ~/.mds3

And then fetch the `primary` database off localhost and place it on the bucket
"mydomain"

$: %(prog)s -d primary -b mydomain

And it would be zipped despite not specifying it.

We can go a step further by setting up sections to do specific backups, and
then calling them by name. First, add your default values and your custom
sections to your configuration file

$: echo '[DEFAULT]
host = db.mydomain.com
user = db_user
password = db_password
bucket = mydomain
zip = true

[primary]
database = primary
key = backups/primary_%%Y%%m%%d%%H%%M%%S.sql.gz

[secondary]
database = secondary1 secondary2
key = backups/secondary_%%Y%%m%%d%%H%%M%%S.sql.gz
' > ~/.mds3

Then, by running

$: %(prog)s primary

%(prog)s would fetch all the data in the `primary` DB of db.mydomain.com and
put it on S3 at mydomain:backups/backups/primary_202305135500.sql.gz. Or we
could run

$: %(prog)s primary secondary

and %(prog)s Would run each section one at a time, adding both files to S3.
Because the host and bucket names are the same for both, we add them to the
DEFAULT section so we don't have to repeat them.

The same is true for all arguments. Any section requested will first be set by
the values in DEFAULT, then merged with its own values, as well as anything run
from the command line. Using them all together in this way we can make singular
sections that can be used for several different backups.

For example, the following could be run once a year

$: %(prog)s primary -k backups/primary_yearly_%%Y.sql.gz

And if we wanted to run monthly backups and keep them forever, we could

$: %(prog)s primary -k backups/primary_monthly_%%Y%%M.sql.gz

But if you wanted to overwrite the monthly backups after a year, so that we
only ever have a maximum of the last twelve (12) months, we could

$: %(prog)s primary -k backups/primary_monthly_%%M.sql.gz

Removing the year from the key name ensures that the second time the same key
is generated, a year later, the data in S3 will be overwritten. In this way, we
still only need to set the host/user/pass once, in DEFAULT, and we only need to
specify the database(s) once per section, but we continue to have a wealth of
flexibility without the need to write out and maintain a hundred sections just
for every little tweak
"""