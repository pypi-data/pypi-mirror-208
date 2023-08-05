from setuptools import setup, find_packages
import re
import os


PACKAGE_DIR = os.path.join(os.getcwd(), 'watchtower_browser_testing')
with open(os.path.join(PACKAGE_DIR, 'version.py')) as version_file:
    verstrline = version_file.read().strip()
VSRE = r'^__version__ = [\']([0-9\.]*)[\']'
mo = re.search(VSRE, verstrline, re.M)
if mo:
    VERSION = mo.group(1)
else:
    raise Exception('No version string found')


with open('README.md') as readme_file:
    README = readme_file.read()

setup_args = dict(
    name='watchtower_browser_testing',
    version=VERSION,
    description='Watchtower in-browser tracking testing library, based on Playwright',
    license='MIT',
    packages=find_packages(),
    author='Jacob Noordmans',
    author_email='jacob@graindataconsultants.com',
    keywords=['Watchtower'],
    package_data={'watchtower_browser_testing': ['templates/*.html']}
)

install_requires = [
    'playwright==1.32.1',
    'Cerberus',
    'marko',
    'Jinja2',
    'pytz',
    'tzlocal'
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)