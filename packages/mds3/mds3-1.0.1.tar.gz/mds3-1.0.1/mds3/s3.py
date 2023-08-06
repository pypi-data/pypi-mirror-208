# coding=utf8
"""SSS (S3) Module

Various helper functions for using S3
"""

__author__		= "Chris Nasr"
__copyright__	= "OuroborosCoding"
__maintainer__	= "Chris Nasr"
__email__		= "chris@ouroboroscoding.com"
__created__		= "2023-05-12"

# Limit exports
__all__ = [ 'put' ]

# Import python modules
from time import sleep

# Import pip modules
import boto3
from botocore.client import Config as BotoConfig
from botocore.exceptions import ClientError
from botocore.vendored.requests.packages.urllib3.exceptions import ReadTimeoutError

# Constants
MAX_TIMEOUTS = 5

class S3Exception(Exception):
	pass

def put(info):
	"""Put

	Takes a file and puts it onto S3 as a private file

	Arguments:
		info (dict): All info required to place the file in the correct place in
						the correct bucket on S3

	Returns:
		None
	"""

	# Create a new session using the profile
	s3_session = boto3.Session(profile_name=info.profile)

	# Get an S3 resource
	s3_resource = s3_session.resource('s3', config=BotoConfig(**{
		'connect_timeout': 5,
		'read_timeout': 2
	}))

	# Get a client
	s3_client = s3_session.client(
		's3',
		config=boto3.session.Config(
			s3={'addressing_style': 'path'},
			signature_version='s3v4'
		)
	)

	# Set the headers
	headers = {
		'ACL': 'private',
		'Body': info.content,
		'ContentType': info.zip and 'application/gzip' or 'text/plain',
		'ContentLength': len(info.content)
	}

	# Keep trying if we get timeout errors
	iTimeouts = 0
	while True:

		# Create new object and upload it
		try:
			return s3_resource.Object(info.bucket, info.key).put(**headers)

		# Check for client Errors
		except ClientError as e:
			raise S3Exception(e.args, info.bucket, info.key)

		except ReadTimeoutError as e:
			iTimeouts += 1					# increment the timeout count
			if iTimeouts >= MAX_TIMEOUTS:	# if too many timeouts
				raise S3Exception('S3 not available', str(e))
			sleep(1)						# else sleep for a second
			continue						# and try again

		except Exception as e:
			raise S3Exception('Unknown S3 exception', str(e))