import pygame

from sprites import *
from settings import *


class State():
	"""Base class for State.

	It implements the two basic functions:
		-enter_state(): add the current state to the stack.
		-exit_state(): pop the state out of the stack
	
	A valid state implements three additional functions:
		-update(dt, events): this function iterates over the events in that particular state.
		-handle_event(dt, event): this function handles a particular event.
		-render(surface): this function renders the state.
	"""
	def __init__(self, game):
		self.game = game
		self.prev_state = None

	def update(self, dt, events):
		for event in events:
			self.handle_event(dt, event)

	def render(self, surface):
		pass
	
	def handle_event(self, dt, event):
		if event.type == pygame.QUIT:
			self.game.running, self.game.playing = False, False

	def enter_state(self):
		if len(self.game.state_stack) >= 1:
			self.prev_state = self.game.state_stack[-1]
		self.game.state_stack.append(self)
    
	def exit_state(self):
		self.game.state_stack.pop()


class MainMenu(State):
	"""MainMenu state.
	
	It implements the main menu.
	
	-Play
	-Ranking
	-Credits
	
	This is the starting state.
	Transition state:
        1) GO TO PLAYING_STATE if Play is selected
		2) GO TO RANKING_STATE if Ranking is selected
		3) GO TO CREDITS_STATE if Cresits is selected
	
	"""
	def __init__(self, game):
		self.game = game
	    # Menu
		self.menu_color = (255, 255, 255) # WHITE
		self.menu_options = {0: "Play", 1: "Ranking", 2: "Credits"}
		self.index = 0
		# Cursor
		self.cursor_color = (0, 0, 255)
		self.cursor_rect = pygame.Rect(0, 0, 30, 30)
		self.cursor_pos_y = GAME_H//2 - 15
		self.cursor_rect.x, self.cursor_rect.y = GAME_W//4 + 10, self.cursor_pos_y
		# Create sprites
		self.sprites = pygame.sprite.Group()
		bg = Background(self.sprites, self.game.graphics_dir + "/environment/background.png")
		ground = Ground(self.sprites, self.game.graphics_dir + "/environment/ground.png", bg.scale_factor)
		# State
		self.trigger_state = False

		self.game.music.play(loops=-1)


	def update(self, dt, events):
		super().update(dt, events)
		self.sprites.update(dt)
		self.transition_state()
	
	def handle_event(self, dt, event):
		super().handle_event(dt, event)
		# If pressed a key
		if event.type == pygame.KEYDOWN:
			# update the cursor
			self.update_cursor(event.key)
			if event.key == pygame.K_RETURN:
				self.trigger_state = True

	def update_cursor(self, key):
		# Check the key
		if key == pygame.K_DOWN:
			self.index = (self.index + 1) % len(self.menu_options)
		elif key == pygame.K_UP:
			self.index = (self.index - 1) % len(self.menu_options)
		self.cursor_rect.y = self.cursor_pos_y + (self.index * 32)
	
	def transition_state(self):
		# If Play is selected, go to PLAY_STATE
		if self.menu_options[self.index] == "Play" and self.trigger_state:
			new_state = GameWorld(self.game)
			new_state.enter_state()
		elif self.menu_options[self.index] == "Ranking" and self.trigger_state:
			new_state = RankingMenu(self.game)
			new_state.enter_state()
		elif self.menu_options[self.index] == "Credits" and self.trigger_state:
			new_state = CreditsMenu(self.game)
			new_state.enter_state()
		self.trigger_state = False
	
	def render_options(self, surface):
		for index, val in zip(range(len(self.menu_options)), self.menu_options.values()):
			y = GAME_H//2 + index * 32
			self.game.draw_text(surface, str(val), (0, 0, 0), GAME_W//2, y)
	
	def render(self, surface):
		# Black
		surface.fill((0, 0, 0))
		# Sprites
		self.sprites.draw(surface)
		# Menu
		self.game.draw_text(surface, "Flappy Bird", (0, 0, 0), GAME_W//2, GAME_H//4)
		# Cursor
		pygame.draw.rect(surface, self.cursor_color, self.cursor_rect)
		# Menu
		self.render_options(surface)


class RankingMenu(State):
	def __init__(self, game):
		super(RankingMenu, self).__init__(game)
		self.game.load_score()

	def update(self, dt, events):
		super().update(dt, events)
		self.prev_state.sprites.update(dt)
	
	def handle_event(self, dt, event):
		super().handle_event(dt, event)
		# If pressed a key
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_RETURN:
				self.exit_state()

	def render(self, surface):
		# Black
		surface.fill((0, 0, 0))
		# Sprites
		self.prev_state.sprites.draw(surface)	
		if bool(self.game.sl_manager.ranking):
			for i, (k, v) in enumerate(zip(self.game.sl_manager.ranking.keys(), self.game.sl_manager.ranking.values())):
				text = str(len(self.game.sl_manager.ranking) - i) + ". " + str(k) + ": " + str(v)
				pos_y = GAME_H//2 - i * 32
				self.game.draw_text(surface, text, (0, 0, 0), GAME_W//2, pos_y)
		else:
			self.game.draw_text(surface, "There are no ranking yet !", (0, 0, 0), GAME_W//2, GAME_H//2)


class CreditsMenu(State):
	def __init__(self, game):
		super(CreditsMenu, self).__init__(game)
	
	def update(self, dt, events):
		super().update(dt, events)
		self.prev_state.sprites.update(dt)
	
	def handle_event(self, dt, event):
		super().handle_event(dt, event)
		# If pressed a key
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_RETURN:
				self.exit_state()
	
	def render(self, surface):
		# Black
		surface.fill((0, 0, 0))
		# Sprites
		self.prev_state.sprites.draw(surface)	
		self.game.draw_text(surface, "CREDITS", (0, 0, 0), GAME_W//2, GAME_H//2 - 15)
		self.game.draw_text(surface, "made by Norman Marlier", (0, 0, 0), GAME_W//2, GAME_H//2 + 30)


class GameWorld(State):
	"""GameWorld state.
	
	It implements the playing world.
	
	Transition state:
        1) GO TO PAUSE_STATE if pause action is selected
		2) GO TO LOOSE_STATE if failure is trigger
	
	"""
	def __init__(self, game):
		self.game = game

		# Create sprites
		self.all_sprites = pygame.sprite.Group()
		self.player = pygame.sprite.Group()
		self.collision_sprites = pygame.sprite.Group()
		bg = Background(self.all_sprites, self.game.graphics_dir + "/environment/background.png")
		self.scale_factor = bg.scale_factor
		Ground([self.all_sprites, self.collision_sprites], self.game.graphics_dir + "/environment/ground.png", self.scale_factor)
		self.reset()
		# Timer Event 
		self.obstacle_timer = pygame.USEREVENT + 1
		pygame.time.set_timer(self.obstacle_timer, 1400)

		# State
		self.go_to_pause = False
		self.go_to_fail = False
	
	def update(self, dt, events):
		super().update(dt, events)
		self.all_sprites.update(dt)
		self.player.update(dt)
		self.check_collision()
		self.game.update_score()
		self.transition_state()
	
	def handle_event(self, dt, event):
		super().handle_event(dt, event)
		# If pressed a key
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				self.go_to_pause = True
			if event.key == pygame.K_SPACE:
				self.plane.jump()
		if event.type == self.obstacle_timer:
			Obstacle([self.all_sprites, self.collision_sprites], self.game.graphics_dir + "/obstacles")
	
	def check_collision(self):
		if pygame.sprite.spritecollide(self.plane, self.collision_sprites, False, pygame.sprite.collide_mask) \
		or self.plane.rect.top <= 0:
			self.plane.kill()
			for sprite in self.collision_sprites.sprites():
				if sprite.sprite_type == 'obstacle':
					sprite.kill()
			self.go_to_fail = True
			
	def render(self, surface):
		# Black
		surface.fill((0, 0, 0))
		# Sprites
		self.all_sprites.draw(surface)
		self.game.draw_text(surface, str(self.game.score), (0, 0, 0), GAME_W//2, GAME_H//10)
		self.player.draw(surface)
		
	def transition_state(self):
		# If go_to_fail -> FailState
		if self.go_to_fail:
			new_state = FailedMenu(self.game)
			new_state.enter_state()
			self.go_to_fail = False
		# Elif go_to_pause -> PauseState
		elif self.go_to_pause and not self.go_to_fail:

			new_state = PauseMenu(self.game)
			new_state.enter_state()
			self.go_to_pause = False
	
	def reset(self):
		self.game.reset_score()
		self.plane = Plane(self.player, self.game.graphics_dir + "/plane", self.game.sound_dir, self.scale_factor / 1.7)


class FailedMenu(State):
	"""This class handles the state where the player fails.
	
	Possess only Exit state.
	"""
	def __init__(self, game):
		self.game = game

		# Menu
		self.menu_surf = pygame.image.load(self.game.graphics_dir + "/ui/menu.png").convert_alpha()
		self.menu_rect = self.menu_surf.get_rect(center=(GAME_W//2, GAME_H//2))
	
	def update(self, dt, events):
		super().update(dt, events)
		self.prev_state.all_sprites.update(dt)
	
	def handle_event(self, dt, event):
		super().handle_event(dt, event)
		# If pressed a key
		if event.type == pygame.KEYDOWN:
			# update the cursor
			if event.key == pygame.K_ESCAPE:
				self.game.save_score()
				# Put the plane at the beginning
				self.prev_state.reset()
				self.exit_state()
	
	def render(self, surface):
		# Black
		surface.fill((0, 0, 0))
		self.prev_state.all_sprites.draw(surface)
		surface.blit(self.menu_surf, self.menu_rect)
		self.game.draw_text(surface, str(self.game.score), (0, 0, 0), GAME_W//2, GAME_H//2 + self.menu_rect.height)


class PauseMenu(State):
	def __init__(self, game):
		super(PauseMenu, self).__init__(game)
		self.trigger_state = False
		# Color
		self.menu_color = (0, 0, 0)
		# Rectangle
		self.menu_rect = pygame.Rect(0, 0, GAME_W//2, GAME_H//2)
		self.menu_rect.center = (GAME_W//2, GAME_H//2)
		# Set the menu options
		self.menu_options = {0: "Restart", 1: "Exit"}
		self.index = 0
		self.index_pos = {0: -1, 1: 1}
		# Cursor
		self.cursor_color = (255, 255, 255)
		self.cursor_rect = pygame.Rect(0, 0, 20, 20)
		self.cursor_pos_y = self.menu_rect.centery - self.cursor_rect.width/2
		self.cursor_rect.x, self.cursor_rect.y = self.menu_rect.left + 10, self.cursor_pos_y + self.index_pos[self.index] * 32
	
	def update(self, dt, events):
		super().update(dt, events)
		self.transition_state()
	
	def handle_event(self, dt, event):
		super().handle_event(dt, event)
		# If pressed a key
		if event.type == pygame.KEYDOWN:
			# update the cursor
			self.update_cursor(event.key)
			if event.key == pygame.K_RETURN:
				self.trigger_state = True
	
	def update_cursor(self, key):
		if key == pygame.K_DOWN:
			self.index = (self.index + 1) % len(self.menu_options)
		elif key == pygame.K_UP:
			self.index = (self.index - 1) % len(self.menu_options)
		self.cursor_rect.y = self.cursor_pos_y + (self.index_pos[self.index] * 32)
	
	def transition_state(self):
		if self.menu_options[self.index] == "Restart" and self.trigger_state:
			self.trigger_state = False
			self.exit_state()
		elif self.menu_options[self.index] == "Exit" and self.trigger_state:
			self.game.save_score()
			self.trigger_state = False
			while len(self.game.state_stack) > 1:
				self.game.state_stack.pop()
	
	def render_menu(self, surface):
		# TODO: better way to do that
		for index, val in zip(range(len(self.menu_options)), self.menu_options.values()):
			y = self.menu_rect.centery + self.index_pos[index] * 32
			self.game.draw_text(surface, str(val), (255, 255, 255), self.menu_rect.centerx, y)

	def render(self, surface):
		self.prev_state.render(surface)
		pygame.draw.rect(surface, self.menu_color, self.menu_rect)
		pygame.draw.rect(surface, self.cursor_color, self.cursor_rect)
		self.render_menu(surface)
		
