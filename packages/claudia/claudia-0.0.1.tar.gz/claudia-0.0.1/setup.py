import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

current_directory = os.path.dirname(os.path.abspath(__file__))
try:
    with open(os.path.join(current_directory, 'src/claudia/README.md'), encoding='utf-8') as f:
        long_description = f.read()
except Exception:
    long_description = ''

def read_requirements():
    with open('requirements.txt') as req:
        content = req.read()
        requirements = content.split('\n')

    return requirements


setup(
    name='claudia',
    version='0.0.1',
    description='Run XRPL Automated Tests',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    author="Kausty Saxena",
    author_email="ksaxena@ripple.com",
    keywords="ripple xrpl python javascript",
    url='https://xrpl.org/',
    download_url='https://gitlab.ops.ripple.com/xrpledger/xrpl-nocode-automation',
    py_modules=['claudia.claudia'],
    install_requires=read_requirements(),
    packages=['claudia'],
    package_dir={"claudia": "src/claudia"},
    package_data={'claudia': [
        "./requirements.txt"
        "./README.md",
        "./features/*.feature",
        "./javascript/*.js",
        "./javascript/features/*.js",
        "./javascript/features/lib/*.js",
        "./javascript/features/steps/*.js",
        "./javascript/cleanup",
        "./javascript/package.json",
        "./javascript/package-lock.json",
        "./javascript/runSetup",
        "./javascript/runTest",
        "./python/*.py",
        "./python/behave.ini",
        "./python/cleanup",
        "./python/features/*.py",
        "./python/features/exceptions/*.py",
        "./python/features/lib/*.py",
        "./python/features/steps/*.py",
        "./python/runSetup",
        "./python/runTest",
    ]},
    include_package_data=True,
    entry_points='''
        [console_scripts]
        claudia=claudia.claudia:main
    '''
)
