from setuptools import setup, find_packages

version = '0.2.2dev'

setup(
    name='webpy-mongodb-sessions',
    version=version,
    description='Implements a MongoDB-backed session store for web.py',
    keywords='web.py mongodb',
    author='Steven Anderson',
    author_email='steve@whilefalse.net',
    url='https://github.com/whilefalse/webpy-mongodb-sessions',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'distribute',
        'web.py',
        'pymongo',
        ],
    package_data = {
        # if any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
        },
    )
