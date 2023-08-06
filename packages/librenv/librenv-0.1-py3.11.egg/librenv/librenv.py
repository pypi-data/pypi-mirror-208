from threading import Thread
from sdl2.sdlimage import IMG_INIT_JPG, IMG_INIT_PNG, IMG_INIT_WEBP, IMG_Init
from sdl2.ext import fill
from sdl2 import *
import ctypes
import time
import os

from .project import Project
from .api.sprite import Sprite

class LibreNV:

    def __init__(self):
        # Initialize video
        SDL_Init(SDL_INIT_EVERYTHING)
        IMG_Init(IMG_INIT_JPG | IMG_INIT_PNG | IMG_INIT_WEBP)
        
        # Make window
        self.window = SDL_CreateWindow(b"LibreNV",
                                       SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                                       800, 600, SDL_WINDOW_SHOWN)
        self.windowsurface = SDL_GetWindowSurface(self.window)
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

    def get_drawables(self):
        return Sprite.SPRITES

    def draw_background(self):
        fill(self.windowsurface, 0)

    def draw(self):
        self.draw_background()
        drawables = self.get_drawables()
        for drawable in drawables:
            if drawable.is_hidden: continue
            SDL_BlitSurface(drawable.image, None, self.windowsurface, 
                            SDL_Rect(drawable.position.x, drawable.position.y)
            )
        SDL_UpdateWindowSurface(self.window)

    def check_events(self):
        event = SDL_Event()
        while SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == SDL_QUIT:
                self.running = False
                break

    def loop(self):
        while self.running:
            self.check_events()
            self.draw()
            time.sleep(0.016)

        SDL_DestroyWindow(self.window)
        SDL_Quit()
        return 0


