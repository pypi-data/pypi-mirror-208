import importlib
import json
import sys
import os

from .api.vector2 import Vector2

class Project:

    def __init__(self, project_dir, name, version, main, resource_dir, texts_dir, images_dir, audio_dir, fonts_dir, resolution):
        self.name           = name
        self.version        = version
        self.main           = main
        self.resource_dir   = resource_dir
        self.texts_dir      = texts_dir
        self.images_dir     = images_dir
        self.audio_dir      = audio_dir
        self.fonts_dir      = fonts_dir
        self.resolution     = Vector2(resolution["x"], resolution["y"])

        self.extension = '.py'
        self.project_dir = project_dir
        sys.path.append(self.project_dir)

        self._main_module = self.get_main_module()
        self._main_func   = self.get_main_func()
       
    def inspect_module(self, obj) -> bool:
        return hasattr(obj, "main")

    def get_main_func(self):
        return getattr(self._main_module, "main")

    def get_main_module(self):
        for file in os.listdir(self.project_dir):
            if file.endswith(self.extension) and file == self.main:
                modulename = file[:-3]
                pfile = importlib.import_module(modulename)
                if self.inspect_module(pfile):
                    return pfile

    def run(self):
        self._main_func()

    @staticmethod
    def from_file(file_path):
        file = open(file_path, "r")
        data = json.loads(file.read())
        return Project(
            project_dir     = os.path.dirname(file_path),
            name            = data['name'],
            version         = data['version'],
            main            = data['main'],
            resource_dir    = data['resource_dir'],
            texts_dir       = data['text_dir'],
            images_dir      = data['images_dir'],
            audio_dir       = data['audio_dir'],
            fonts_dir       = data['fonts_dir'],
            resolution      = data['resolution']
        )

