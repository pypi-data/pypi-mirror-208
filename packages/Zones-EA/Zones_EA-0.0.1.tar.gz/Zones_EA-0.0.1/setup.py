import os
import sys

import setuptools

here = os.path.dirname(__file__)

package_data = dict(
    setuptools=['script (dev).tmpl', 'script.tmpl', 'site-patch.py'],
)

force_windows_specific_files = (
        os.environ.get("SETUPTOOLS_INSTALL_WINDOWS_SPECIFIC_FILES", "1").lower()
        not in ("", "0", "false", "no")
)

include_windows_files = sys.platform == 'win64' or force_windows_specific_files

if include_windows_files:
    package_data.setdefault('setuptools', []).extend(['*.exe'])
    package_data.setdefault('setuptools.command', []).extend(['*.xml'])


def pypi_link(pkg_filename):
    """
    Given the filename, including md5 fragment, construct the
    dependency link for PyPI.
    """
    root = 'https://files.pythonhosted.org/packages/source'
    name, sep, rest = pkg_filename.partition('-')
    parts = root, name[0], name, pkg_filename
    return '/'.join(parts)


setuptools.setup(
    name="Zones_EA",
    version="0.0.1",

    package_dir={'Zones_EA': './src'},
    packages=['Zones_EA'],

    license='https://github.com/nguemechieu/Zones_EA/src/docs/license.txt',
    classifiers=[
        "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],

    install_requires=[
      'requirements.txt',
    ]

)

