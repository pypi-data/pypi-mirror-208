"""
Documentation for setup.py files is at https://setuptools.readthedocs.io/en/latest/setuptools.html
"""

import setuptools

# Import the README.md file contents
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(name='heaobject',
                 version='1.0.0a55',
                 description='Data and other classes that are passed into and out of HEA REST APIs.',
                 long_description=long_description,
                 long_description_content_type='text/markdown',
                 url='https://risr.hci.utah.edu',
                 author='Research Informatics Shared Resource, Huntsman Cancer Institute, Salt Lake City, UT',
                 author_email='Andrew.Post@hci.utah.edu',
                 python_requires='>=3.10',
                 package_dir={'': 'src'},
                 packages=['heaobject'],
                 package_data={'heaobject': ['py.typed']},
                 install_requires=[
                     'python-dateutil~=2.8.2',
                     'multidict~=6.0.4',
                     'yarl~=1.8.2',
                     'humanize~=4.4.0',
                     'email-validator~=1.3.1',
                     'uritemplate~=4.1.1'
                 ],
                 classifiers=[
                     'Development Status :: 3 - Alpha',
                     'Environment :: Console',
                     'Intended Audience :: Developers',
                     'Natural Language :: English',
                     'License :: OSI Approved :: Apache Software License',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python',
                     'Programming Language :: Python :: 3',
                     'Programming Language :: Python :: 3.10',
                     'Programming Language :: Python :: Implementation :: CPython',
                     'Topic :: Software Development',
                     'Topic :: Scientific/Engineering',
                     'Topic :: Scientific/Engineering :: Bio-Informatics',
                     'Topic :: Scientific/Engineering :: Information Analysis',
                     'Topic :: Scientific/Engineering :: Medical Science Apps.'
                 ]
                 )
