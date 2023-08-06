#!/usr/bin/env python3

from setuptools import setup

with open('README.md') as f:
    long_description = f.read()


setup(
    name='firmetix',
    packages=['firmetix'],
    install_requires=['pyserial', 'simplepyble'],

    version='7.0.2',
    description="Remotely Control And Monitor Arduino and Esp devices",
    long_description=long_description,
    long_description_content_type='text/markdown',

    author='Nils Lahaye',
    author_email='nils.lahaye@icloud.com',
    url='https://github.com/Nilon123456789/firmetix',
    download_url='https://github.com/Nilon123456789/firmetix',
    keywords=['firmetix', 'Arduino', 'Protocol', 'Python'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)