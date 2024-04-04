import pygame
from sys import exit
from random import randint, choice

class Player(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		player_walk_1 = pygame.image.load('graphics/player/player_walk_1.png').convert_alpha()
		player_walk_2 = pygame.image.load('graphics/player/player_walk_2.png').convert_alpha()
		self.player_walk = [player_walk_1,player_walk_2]
		self.player_index = 0
		self.player_jump = pygame.image.load('graphics/player/jump.png').convert_alpha()

		self.image = self.player_walk[self.player_index]
		self.rect = self.image.get_rect(midbottom = (80,300))
		self.gravity = 0

		self.jump_sound = pygame.mixer.Sound('audio/jump.mp3')
		self.jump_sound.set_volume(0.5)

	def player_input(self):
		keys = pygame.key.get_pressed()
		if keys[pygame.K_SPACE] and self.rect.bottom >= 300:
			self.gravity = -15.5
			self.jump_sound.play()

	def apply_gravity(self):
		self.gravity += 1
		self.rect.y += self.gravity
		if self.rect.bottom >= 300:
			self.rect.bottom = 300

	def animation_state(self):
		if self.rect.bottom < 300: 
			self.image = self.player_jump
		else:
			self.player_index += 0.1
			if self.player_index >= len(self.player_walk):self.player_index = 0
			self.image = self.player_walk[int(self.player_index)]

	def update(self):
		self.player_input()
		self.apply_gravity()
		self.animation_state()

class Obstacle(pygame.sprite.Sprite):
	def __init__(self,type):
		super().__init__()
		
		if type == 'fly':
			fly_1 = pygame.image.load('graphics/fly/fly1.png').convert_alpha()
			fly_2 = pygame.image.load('graphics/fly/fly2.png').convert_alpha()
			self.frames = [fly_1,fly_2]
			y_pos = 200
		else:
			snail_1 = pygame.image.load('graphics/snail/snail1.png').convert_alpha()
			snail_2 = pygame.image.load('graphics/snail/snail2.png').convert_alpha()
			self.frames = [snail_1,snail_2]
			y_pos  = 300

		self.animation_index = 0
		self.image = self.frames[self.animation_index]
		self.rect = self.image.get_rect(midbottom = (randint(900,1100),y_pos))

	def animation_state(self):
		self.animation_index += 0.1 
		if self.animation_index >= len(self.frames): self.animation_index = 0
		self.image = self.frames[int(self.animation_index)]

	def update(self):
		self.animation_state()
		self.rect.x -= 6
		self.destroy()

	def destroy(self):
		if self.rect.x <= -100: 
			self.kill()

def display_score():
    current_time = int(pygame.time.get_ticks() / 1000) - start_time
    score_surf = test_font.render(f'Score: {current_time}', False, (64, 64, 64))
    score_rect = score_surf.get_rect(center=(400, 40))
    screen.blit(score_surf, score_rect)
    return current_time

def collision_sprite():
    if pygame.sprite.spritecollide(player.sprite, obstacle_group, False):
        obstacle_group.empty()
        return False
    else:
        return True

# 최고 점수를 파일에서 읽어오는 함수
def read_high_score():
    try:
        with open('score.txt', 'r') as file:
            content = file.read()
            if content:
                high_score = int(content)
            else:
                high_score = 0
    except FileNotFoundError:
        # 파일이 없으면 0으로 초기화
        high_score = 0
    return high_score

# 현재 점수를 파일에 저장하는 함수
def save_high_score(score):
    with open('score.txt', 'w') as file:
        file.write(str(score))

pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption('Runner')
clock = pygame.time.Clock()
test_font = pygame.font.Font('font/Pixeltype.ttf', 50)
game_active = False
start_time = 0
score = 0
bg_music = pygame.mixer.Sound('audio/music.wav')
game_over_sound = pygame.mixer.Sound('audio/gameover.mp3')
endcount = 0

# Groups
player = pygame.sprite.GroupSingle()
player.add(Player())

obstacle_group = pygame.sprite.Group()

sky_surface = pygame.image.load('graphics/Sky.png').convert()
ground_surface = pygame.image.load('graphics/ground.png').convert()

# Intro screen
player_stand = pygame.image.load('graphics/player/player_stand.png').convert_alpha()
player_stand = pygame.transform.rotozoom(player_stand, 0, 2)
player_stand_rect = player_stand.get_rect(center=(400, 200))

game_name = test_font.render('Mario Runner', False, (111, 196, 169))
game_name_rect = game_name.get_rect(center=(400, 80))

game_message = test_font.render('Press rshift to run', False, (240, 230, 140))
game_message_rect = game_message.get_rect(center=(400, 330))

# Timer
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1500)

# 게임 속도를 조절하기 위한 변수
obstacle_speed = 6
groundx = 0
# 게임 시작 전에 최고 점수를 로드하고 표시
high_score = read_high_score()
high_score_text = test_font.render(f'Best Score: {high_score}', False, (111, 196, 169))
high_score_rect = high_score_text.get_rect(center=(400, 70))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if game_active:
            if event.type == obstacle_timer:
                obstacle_group.add(Obstacle(choice(['fly', 'snail', 'snail', 'snail'])))
                # 게임 속도를 점점 빠르게
                obstacle_speed += 0.3

        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RSHIFT:
                if endcount == 1:
                    game_active = False
                    endcount = 0
                    score = 0
                    obstacle_group.empty()
                    obstacle_speed = 6
                    player.sprite.rect.midbottom = (80, 300)
                    bg_music.play(loops=-1)
                    start_time = int(pygame.time.get_ticks() / 1000)
                game_active = True
                start_time = int(pygame.time.get_ticks() / 1000)
                game_over_sound.stop()
                bg_music.play(loops=-1)
    if game_active:
        screen.blit(sky_surface, (groundx, 0))
        screen.blit(sky_surface, (groundx + 800, 0))
        # 그라운드를 그리고 이동
        screen.blit(ground_surface, (groundx, 300))
        screen.blit(ground_surface, (groundx + 800, 300))

        # 그라운드 이동 속도 설정
        groundx -= int(obstacle_speed)

        # 그라운드가 일정 수준 이상 옆으로 이동하면 다시 원래의 자리로 이동
        if groundx <= -800:
            groundx = 0
            
        score = display_score()

        player.draw(screen)
        player.update()

        # 장애물의 이동 속도를 업데이트
        for obstacle in obstacle_group:
            obstacle.rect.x -= int(obstacle_speed)


        obstacle_group.draw(screen)
        obstacle_group.update()

        game_active = collision_sprite()

    else:
        screen.fill((94, 129, 162))
        screen.blit(player_stand, player_stand_rect)

        # 현재 점수 표시
        score_message = test_font.render(f'Your score: {score}', False, (111, 196, 169))
        score_message_rect = score_message.get_rect(center=(400, 370))
        screen.blit(score_message, score_message_rect)

        # 최고 점수 표시
        screen.blit(high_score_text, high_score_rect)

        if score == 0:
            screen.blit(game_message, game_message_rect)
        else:
            bg_music.stop()
            if endcount == 0:
                game_over_sound.play()
                endcount = 1
                
        # 최고 점수를 넘을 때 파일에 새로운 최고 점수 저장
        if score > high_score:
            high_score = score
            save_high_score(high_score)

    pygame.display.update()
    clock.tick(60)