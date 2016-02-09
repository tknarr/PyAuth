# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from setuptools.command.install import install as _install
from setuptools.command.develop import develop as _develop
# To use a consistent encoding
from codecs import open
from os import path
from glob import glob
import pkg_resources
import pyauth

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Collect icon images for use in data_files
image_files = []
# Icon bundles
files = glob( 'images/*.ico' )
entry = ( 'share/' + pyauth.__program_name__, files )
image_files.append( entry )
# Large program icons
files = glob( 'images/*.png' )
entry = ( 'share/icons/hicolor/512x512/apps', files )
image_files.append( entry )
# Specific sizes of icons
for s in [ 16, 24, 32, 48, 64, 128, 256 ]:
    files = glob( 'images/{0}x{0}/*.png'.format( str(s) ) )
    entry = ( 'share/icons/hicolor/{0}x{0}/apps'.format( str(s) ), files )
    image_files.append( entry )


# Post-installation script
def _post_install( data_path, script_path ):
    # Read in the desktop shortcut template and substitute final paths into it to create
    # the real shortcut file
    template = data_path + '/share/doc/' + pyauth.__program_name__ + '/PyAuth.desktop.in'
    shortcut = data_path + '/share/doc/' + pyauth.__program_name__ + '/PyAuth.desktop'
    with open( template, 'r' ) as tf:
        with open( shortcut, 'w' ) as sf:
            for line in tf:
                l = line.format( program_name = pyauth.__program_name__,
                                 script_path = script_path,
                                 data_path = data_path )
                sf.write( l )


# Classes to add post-install behavior to standard install and develop commands

class my_install( _install ):
    def run( self ):
        _install.run( self )

        # the second parameter, [], can be replaced with a set of parameters if _post_install needs any
        self.execute( _post_install, [ self.install_data, self.install_scripts ], msg="Running post install task" )

class my_develop( _develop ):
    def run( self ):
        self.execute( noop, ( self.install_lib ), msg="Running develop task" )
        _develop.run( self )
        self.execute( _post_install, [ self.install_data, self.install_scripts ], msg="Running post develop task" )


setup(
    name = pyauth.__program_name__,

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version = pyauth.__version__ + pyauth.__version_tag__,

    description = 'Google Authenticator (TOTP) desktop client',
    long_description = long_description,

    # The project's main homepage.
    url = 'https://github.com/tknarr/PyAuth',

    # Author details
    author = 'Todd Knarr',
    author_email = 'tknarr@silverglass.org',

    # Choose your license
    license = 'GPLv3+',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Topic :: Security',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',

        # Other classifiers
        'Environment :: X11 Applications',
        'Operating System :: Unix',
    ],

    # What does your project relate to?
    keywords = 'authentication totp hotp 2fa',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages( exclude = ['contrib', 'docs', 'tests'] ),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires = [
        'pyotp>=2.0.1'
        ],

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    data_files = image_files + [
        ( 'share/doc/' + pyauth.__program_name__,
          [ 'README.rst',
            'LICENSE.html',
            'TODO.md',
            'VERSIONS.md',
            'PyAuth.desktop.in',
            'PyAuth.desktop'
          ] )
        ],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points = {
        'gui_scripts': [
            'PyAuth=pyauth.__main__:main',
        ],
    },
    cmdclass = {
        'install': my_install,  # override install
        'develop': my_develop   # develop is used for pip install -e .
        }
)
