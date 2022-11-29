from setuptools import setup


# Get version from __init__.py file
def get_version():
    with open('zion/__init__.py') as f:
        version = {}
        for line in f:
            if line.startswith('version'):
                exec(line, version)

        return version['version']


setup(
    name='zion',
    url='https://github.com/reallygoodnickname/zion',
    license='GNU General Public License v3.0',
    version=get_version(),
    author='reallygoodnickname',
    author_email='78232370+reallygoodnickname@users.noreply.github.com',
    description='Simple CMS developed solely for practice purposes',
    entry_points={
        'console_scripts': [
            'zionctl= zion.zionctl:run',
        ],
    },
    packages=['zion'],
    package_data={'zion': ['templates/**', 'static/*/*']}
)
