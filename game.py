import pygame
import time
import json
from states import MainMenu
from settings import *



class Game():
    def __init__(self):
        pygame.init()

        # Screen
        self.game_canvas = pygame.Surface((GAME_W, GAME_H))
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Flappy Bird")

        # Time
        self.dt: float = time.time()
        self.prev_dt: float = self.dt
        self.clock = pygame.time.Clock()

        # Events
        self.events = None

        # Assets
        self.load_assets()

        # Data which needs to be store
        self.player_name: str = "player_1"
        self.reset_score()
        self.sl_manager = SaveLoadManager()

        # State
        self.state_stack = []
        self.running: bool = True
        self.playing: bool = False
        self.init_state()
    
    def game_loop(self) -> None:

        while self.playing:
            # Update time
            self.get_dt()
            # Update events
            self.events = pygame.event.get()
            #print(self.state_stack[-1])
            # Update state
            self.update()
            # Render state
            self.render()
            # FPS
            self.clock.tick(FRAMERATE)
    
    def get_dt(self) -> None:
        now = time.time()
        self.dt = now - self.prev_dt
        self.prev_dt = now
    
    def update(self) -> None:
        self.state_stack[-1].update(self.dt, self.events)
    
    def render(self) -> None:
        self.state_stack[-1].render(self.game_canvas)
        self.screen.blit(pygame.transform.scale(self.game_canvas, (SCREEN_W, SCREEN_H)), (0, 0))
        pygame.display.flip()  
    
    def init_state(self):
        # First state is the MainMenu
        self.state_stack.append(MainMenu(self))
    
    def draw_text(self, surface, text, color, x, y):
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        surface.blit(text_surface, text_rect)

    def load_assets(self):
        self.assets_dir = "./assets"
        self.graphics_dir = self.assets_dir + "/graphics"
        self.sound_dir = self.assets_dir + "/sounds"
        self.FONTSIZE = 25
        self.font = pygame.font.Font(self.graphics_dir + '/font/BD_Cartoon_Shout.ttf', self.FONTSIZE)
        # Music 
        self.music = pygame.mixer.Sound(self.sound_dir + '/music.wav')
        self.music.set_volume(0.1)
		
    def reset_score(self):
        self.score: int = 0
        self.start_offset: int = pygame.time.get_ticks()
    
    def update_score(self):
        self.score = (pygame.time.get_ticks() - self.start_offset) // 1000
    
    def load_score(self):
        self.sl_manager.load_data()
    
    def save_score(self):
        self.sl_manager.save_data((self.player_name, self.score))


class SaveLoadManager():
    # Manage ranking
    # Save the top 10 score
    # Remember the name and the associated score
    def __init__(self):
        self.filename = SAVE_FILE
        self.ranking = {}
        self.TOP_N = 10
    
    def sorted_ranking(self, ranking):
        return dict(sorted(ranking.items(), key=lambda item: item[1]))

    def load_data(self):
        try:
            with open(self.filename, "r+") as file:
                self.ranking = json.load(file)
                self.update_ranking(self.ranking)
        except:
            pass
    
    def save_data(self, data):
        """Add the new data to the current ranking."""
        self.update_ranking(data)
        with open(self.filename, "w+") as file:
            json.dump(self.ranking, file)

    def update_ranking(self, data):
        """Check if the new data can be integrated into the ranking
        
        Add the new data and sort the ranking. Then, keep the 10 best.
        Args:
            data, a tuple (name, score)
        """
        # If the player already exists
        if data[0] in self.ranking.keys():
            # Check if the new score is greater than before
            if data[1] > self.ranking[data[0]]:
                self.ranking[data[0]] = data[1]
        else:
            self.ranking[data[0]] = data[1]
        # Sorted the ranking and keep the 10 best
        self.ranking = self.sorted_ranking(self.ranking)
        self.ranking = {kv[0]:kv[1] for i, kv in enumerate(self.ranking.items()) if i <= self.TOP_N}


if __name__ == "__main__":
    g = Game()

    while g.running:
        g.playing = True
        g.game_loop()


