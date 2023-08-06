# Python imports
from setuptools import setup, find_packages
from distutils.util import convert_path

# Shared long description
with open('README.md', 'r') as oF:
	long_description=oF.read()

# Shared version
with open(convert_path('mds3/version.py')) as oF:
	d = {}
	exec(oF.read(), d)
	version = d['__version__']

setup(
	name='mds3',
	version=version,
	description='MySQL Dump to S3',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://ouroboroscoding.com/mds3',
	project_urls={
		'Source': 'https://github.com/ouroboroscoding/mds3',
		'Tracker': 'https://github.com/ouroboroscoding/mds3/issues'
	},
	keywords=['mysql','mysqldump','backup', 's3', 'aws'],
	author='Chris Nasr - OuroborosCoding',
	author_email='chris@ouroboroscoding.com',
	license='MIT',
	packages=['mds3'],
	python_requires='>=3.10',
	install_requires=[
		'boto3>=1.26.79',
		'jobject>=1.0.1',
		'termcolor>=1.1.0'
	],
	entry_points={
		'console_scripts': ['mds3=mds3.__main__:cli']
	},
	zip_safe=True
)