from setuptools import setup, find_packages
import glob
import os
import sys

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('btecli.plugins')

required_packages = [
        'btconfig>=4.4.0,<5.0.0',
        'bs4>=0.0.1,<0.1.0',
        'click>=8.1.3,<9.0.0',
        'click-plugins==1.1.1',
        'colorama==0.4.3',
        'first==2.0.2',
        'jello==1.2.10',
        'lxml==4.9.1',
        'pandas>=2.0.1,<3.0.0',
        'paramiko>=2.11.0,<3.0.0',
        'PyCryptodome>=3.17,<4.0.0',
        'PyYAML>=6.0,<7.0.0',
        'requests>=2.28.1,<2.30.0',
    ]

if '--show-packages' in ' '.join(sys.argv):
    for p in required_packages:
        print(p.split('=')[0])
    sys.exit()    

setup(
    name='btecli',
    version='1.6.4',
    packages=find_packages(),
    include_package_data=True,
    install_requires=required_packages,
    package_data={'': extra_files},
    entry_points='''
        [core_package.cli_plugins]
        [console_scripts]
        ecli=btecli.cli:cli
    ''',
)