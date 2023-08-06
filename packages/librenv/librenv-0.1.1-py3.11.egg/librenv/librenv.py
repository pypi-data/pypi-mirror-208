from threading import Thread
from sdl2.sdlimage import IMG_INIT_JPG, IMG_INIT_PNG, IMG_INIT_WEBP, IMG_Init
from sdl2.sdlttf import TTF_Init
from sdl2.ext import Renderer, init
from sdl2 import *
import ctypes
import time
import os

from .api.drawable import Drawable
from .project import Project

class LibreNV:

    def __init__(self):
        # Initialize SDL 
        init()
        SDL_Init(SDL_INIT_EVERYTHING)
        IMG_Init(IMG_INIT_JPG | IMG_INIT_PNG | IMG_INIT_WEBP)
        TTF_Init()

        # Make window
        self.window = SDL_CreateWindow(b"LibreNV",
                                       SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                                       800, 600, SDL_WINDOW_SHOWN)
        self.windowsurface = SDL_GetWindowSurface(self.window)
        self.renderer = Renderer(self.windowsurface)
        self.running = True
        self.thread = None

    def load_game(self, game_path):
        project_path = game_path + "/project.json"
        if not os.path.exists(project_path):
            return print("project.json not found!")
        project = Project.from_file(project_path)     
        SDL_SetWindowTitle(self.window, bytes(project.name, 'utf-8'))
        self.thread = Thread(target=project.run)
        self.thread.start()
        return self.loop()

    def get_drawables(self) -> list:
        return Drawable.DRAWABLES

    def draw_background(self) -> None:
        self.renderer.clear(SDL_Color(0,0,0))

    def draw(self) -> None:
        self.draw_background()
        drawables = self.get_drawables()
        for drawable in drawables:
            if drawable.is_hidden: continue
            drawable._draw(self.renderer, self.windowsurface)
        self.renderer.present()
        SDL_UpdateWindowSurface(self.window)

    def check_events(self) -> None:
        event = SDL_Event()
        while SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == SDL_QUIT:
                self.running = False
                break

    def loop(self) -> int:
        while self.running:
            self.check_events()
            self.draw()
            time.sleep(0.016)

        SDL_DestroyWindow(self.window)
        SDL_Quit()
        return 0


