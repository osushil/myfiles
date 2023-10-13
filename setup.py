#!/opt/rh/rh-python36/root/bin/python3
from distutils.core import setup
import setuptools
import sys

__authors__ = [
  'Author Name, Company Name'
]
__version__ = '1.2.'
__description__ = "Main Artifact Name"


if '--build' in sys.argv:
    ix = sys.argv.index('--build')
    sys.argv.pop(ix)
    build = sys.argv.pop(ix)
else:
    build = '0'
__version__ = __version__ + str(build)


setup(
    name='ArtifactName',
    version=__version__,
    description=__description__,
    author=", ".join(__authors__),
    packages=['ModuleFolder1', 'ModuleFolder2'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'abcPython1 = ModuleFolder1.PythonFileName1:ModuleName',
            'abcPython2 = ModuleFolder1.PythonFileName2:ModuleName',
            'abcPython3 = ModuleFolder2.PythonFileName1:ModuleName',
            'abcPython4 = ModuleFolder2.PythonFileName2:ModuleName',
        ],
    }
)