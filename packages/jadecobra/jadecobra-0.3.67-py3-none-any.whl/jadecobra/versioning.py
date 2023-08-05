import re
import shutil

from . import toolkit
from . import __version__


class Version(object):

    def __init__(self, library:str=None):
        self.library = library
        self.text = self.read_pyproject()
        self.current_pyproject_version, self.version, self.patch = self.get_pyproject_version()
        self.new_version = f"{self.version}{int(self.patch)+1}"

    @staticmethod
    def pyproject():
        return 'pyproject.toml'

    @staticmethod
    def semantic_version_pattern():
        return r'(\d+[.]\d+[.])(\d+)'

    @staticmethod
    def pyproject_version_pattern():
        return r'version\s+=\s+"((\d+[.]\d+[.])(\d+))"'

    def read_pyproject(self):
        '''Return contents of file'''
        with open(self.pyproject()) as file:
            return file.read()

    def get_pyproject_version(self):
        '''Get version from pyproject.toml'''
        return re.search(
            self.pyproject_version_pattern(),
            self.text
        ).group(1, 2, 3)

    def update_pyproject_version(self):
        '''Update version in pyproject.toml'''
        toolkit.write_file(
            filepath=self.pyproject(),
            data=re.sub(
                self.pyproject_version_pattern(),
                f'version = "{self.new_version}"',
                self.text
            )
        )

    def update_module_version(self):
        '''Update Module Version'''
        toolkit.write_file(
            filepath=f'src/{self.library}/__init__.py',
            data=f'__version__ = "{self.new_version}"',
        )

    @staticmethod
    def remove_dist():
        '''Remove Dist folder for new distribution'''
        try:
            shutil.rmtree('dist')
        except FileNotFoundError:
            'already removed'

    def update(self):
        print(f'updating version to {self.new_version}...')
        self.remove_dist()
        self.update_pyproject_version()
        self.update_module_version()