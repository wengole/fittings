# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from fittings import __version__

install_requires = [
    'django-bootstrap-form',
    'allianceauth>=2.0.5',
    'django-model_utils>=3.1.1',
]

testing_extras = [

]

setup(
    name='aa-fittings',
    version=__version__,
    author='Col Crunch',
    author_email='it-team@serin.space',
    description='A simple fittings and doctrine management application.',
    install_requires=install_requires,
    extras_require={
        'testing': testing_extras,
        ':python_version=="3.4"': ['typing'],
    },
    python_requires='~=3.4',
    license='GPLv3',
    packages=find_packages(),
    url='https://gitlab.com/colcrunch/aa-fittings',
    zip_safe=False,
    include_package_data=True,
)