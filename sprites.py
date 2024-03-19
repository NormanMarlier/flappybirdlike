import pygame
from random import choice, randint

from settings import *



class Background(pygame.sprite.Sprite):
    """This class handles the sprite of the background.
    
    Serves as a animation for MainMenu state and Playing state."""
    def __init__(self, group, img_path: str) -> None:
        super().__init__(group)
        # Type
        self.sprite_type: str = "background"
        # Image
        self.img_path: str = img_path
        bg_img = pygame.image.load(self.img_path).convert()
        self.scale_factor: float = GAME_H / bg_img.get_height()
        full_sized_image = pygame.transform.scale(bg_img, (bg_img.get_width() * self.scale_factor, bg_img.get_height() * self.scale_factor))
        self.image = pygame.Surface((full_sized_image.get_width() * 2 , full_sized_image.get_height()))
        self.image.blit(full_sized_image, (0, 0))
        self.image.blit(full_sized_image, (full_sized_image.get_width(), 0))
        # Position
        self.rect = self.image.get_rect()
        
    def update(self, dt) -> None:
        pos_x = self.rect.x - 250 * dt
        if self.rect.centerx <= 0:
            pos_x = 0
        self.rect.x = round(pos_x)


class Ground(pygame.sprite.Sprite):
    """This class hanles the sprite of the ground.
    
    """
    def __init__(self, group, img_path: str, scale_factor: float) -> None:
        super().__init__(group)
        # type
        self.sprite_type: str = "ground"
        # Image
        self.img_path: str = img_path
        ground_img = pygame.image.load(self.img_path).convert_alpha()
        self.scale_factor: float = scale_factor
        self.image = pygame.transform.scale(ground_img, (ground_img.get_width() * self.scale_factor, ground_img.get_height() * self.scale_factor))
        # Position
        self.rect = self.image.get_rect(bottomleft=(0, GAME_H))
        # Mask
        self.mask = pygame.mask.from_surface(self.image)
        
    def update(self, dt):
        pos_x = self.rect.topleft[0] - 300 * dt
        if self.rect.centerx <= 0:
            pos_x = 0
        self.rect.x = round(pos_x)


class Plane(pygame.sprite.Sprite):
    """This handles the sprite of the plane.
    
    It needs to response to inputs and plays the animation.
    """
    def __init__(self, group, img_dir: str, sound_dir: str, scale_factor: float) -> None:
        super().__init__(group)
        self.sprite_type: str = "plane"
        self.scale_factor: float = scale_factor
		# Image
        self.img_dir: str = img_dir
        # Frames
        self.frames: list = self.import_frames(self.img_dir)
        self.frame_index: float = 0.
        self.image = self.frames[int(self.frame_index)]
        # Rect
        self.rect = self.image.get_rect(midleft=(GAME_W//20, GAME_H//2))
        self.pos = pygame.math.Vector2(self.rect.topleft)
		# Motion
        self.gravity: float = GRAVITY
        self.direction: float = 0.
		# Mask
        self.mask = pygame.mask.from_surface(self.image)
        # Sound
        self.sound_dir: str = sound_dir
        self.jump_sound = pygame.mixer.Sound(self.sound_dir + "/jump.wav")
        self.jump_sound.set_volume(0.12)
        
    def import_frames(self, dir: str) -> list:
        images = [pygame.image.load(dir + f'/red{i}.png') for i in range(3)]
        return [pygame.transform.scale(img, (img.get_width() * self.scale_factor, img.get_height() * self.scale_factor)) for img in images]
    
    def step(self, dt) -> None:
        self.direction += self.gravity * dt
        self.pos.y += self.direction * dt
        self.rect.y = round(self.pos.y)
        
    def animate(self, dt) -> None:
        self.frame_index += 8 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0.
        self.image = self.frames[int(self.frame_index)]

    def rotate(self) -> None:
        rotated_img = pygame.transform.rotozoom(self.image, -self.direction * 0.06, 1.)
        self.image = rotated_img
        self.mask = pygame.mask.from_surface(self.image)
    
    def jump(self) -> None:
        self.jump_sound.play()
        self.direction = -JUMPING_HEIGHT
        
    def update(self, dt) -> None:
        self.step(dt)
        self.animate(dt)
        self.rotate()
        

class Obstacle(pygame.sprite.Sprite):
    """This class handles the sprite of obstacles."""
    def __init__(self, group, img_dir: str):
        super().__init__(group)
        self.sprite_type: str = "obstacle"
        orientation = choice(('up', 'down'))
        self.img_dir: str = img_dir
        surf = pygame.image.load(self.img_dir + f'/{choice((0, 1))}.png').convert_alpha()
        self.image = pygame.transform.scale(surf, pygame.math.Vector2(surf.get_size()))
        
		# Position
        x = GAME_W + randint(40,100)
        if orientation == 'up':
            y = GAME_H + randint(10,50)
            self.rect = self.image.get_rect(midbottom = (x, y))
        else:
            y = randint(-50,-10)
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect = self.image.get_rect(midtop = (x, y))
            
        self.pos = pygame.math.Vector2(self.rect.topleft)

		# Mask
        self.mask = pygame.mask.from_surface(self.image)
        
    def update(self,dt):
        self.pos.x -= 400 * dt
        self.rect.x = round(self.pos.x)
        if self.rect.right <= -100:
             self.kill()

        