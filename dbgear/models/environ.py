import os
from glob import glob


class Environ:

    def __init__(self, project, folder):
        self.project = project
        self.folder = folder
        self.environs = []

    def _get_environs_folder(self):
        return f'{self.folder}/environs'

    def setup(self):
        if not os.path.isdir(self._get_environs_folder()):
            os.mkdir(self._get_environs_folder())

    def read_environs(self):
        for environ in glob(f'{self._get_environs_folder()}/**/mapping.yaml'):
            print(environ)
