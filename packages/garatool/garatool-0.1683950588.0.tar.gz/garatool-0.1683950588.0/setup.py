from setuptools import setup, find_packages


import time
with open('README.md') as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()

version_string = '0.{}.0'.format(int(time.time()))
with open('version.py', 'w') as f:
    f.write(f'version = "{version_string}"')



import time
setup_args = dict(
    name='garatool',
    version=version_string,
    description='GaraSTEM Production Library',
    # long_description_content_type="text/markdown",
    # long_description=README + '\n\n' + HISTORY,
    license='MIT',
    packages=['garatool'],
    author='Curly Nguyen',
    author_email='curly.saigonese@gmail.com',
    keywords=['GaraSTEM'],
    url='https://github.com/curlyz/garatool',
    download_url='https://pypi.org/project/garatool/'
)

install_requires = [
    'termcolor',
    'requests',
    'msgpack',
    'esptool',
    'dacite',
    'colorama'
]

print("find_packages()", find_packages())

import os
if __name__ == '__main__':
    os.system('rm -rf dist')
    setup(**setup_args, install_requires=install_requires)