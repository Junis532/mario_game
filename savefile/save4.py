import pygame
from sys import exit
from random import randint, choice

score = 0

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        player_walk_1 = pygame.image.load('graphics/player/player_walk_1.png').convert_alpha()
        player_walk_2 = pygame.image.load('graphics/player/player_walk_2.png').convert_alpha()
        self.player_walk = [player_walk_1, player_walk_2]
        self.player_index = 0
        self.player_jump = pygame.image.load('graphics/player/jump.png').convert_alpha()
        self.player_sit_1 = pygame.image.load('graphics/player/player_sit_1.png').convert_alpha()
        self.player_sit_2 = pygame.image.load('graphics/player/player_sit_2.png').convert_alpha()

        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom=(80, 300))
        self.gravity = 0

        self.jump_sound = pygame.mixer.Sound('audio/jump.mp3')
        self.jump_sound.set_volume(0.5)

        self.sitting = False
        self.sit_animation_index = 0
        self.sit_animation_speed = 0.1  # Adjust the speed as needed

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= 300:
            self.gravity = -15.5
            self.jump_sound.play()
        elif keys[pygame.K_LSHIFT]:
            self.sitting = True
            # Set the rect position for sitting
            self.rect = self.player_sit_1.get_rect(midbottom=self.rect.midbottom)
        else:
            self.sitting = False
            # Set the rect position for standing
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 300:
            self.rect.bottom = 300

    def animation_state(self):
        if self.sitting:
            self.sit_animation_index += self.sit_animation_speed
            if int(self.sit_animation_index) % 2 == 0:
                self.image = self.player_sit_1
            else:
                self.image = self.player_sit_2
        elif self.rect.bottom < 300:
            self.image = self.player_jump
        else:
            self.player_index += 0.1
            if self.player_index >= len(self.player_walk):
                self.player_index = 0
            self.image = self.player_walk[int(self.player_index)]

    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animation_state()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()

        if type == 'fly':
            fly_1 = pygame.image.load('graphics/fly/fly1.png').convert_alpha()
            fly_2 = pygame.image.load('graphics/fly/fly2.png').convert_alpha()
            self.frames = [fly_1, fly_2]
            y_pos = 250
        else:
            snail_1 = pygame.image.load('graphics/snail/snail1.png').convert_alpha()
            snail_2 = pygame.image.load('graphics/snail/snail2.png').convert_alpha()
            self.frames = [snail_1, snail_2]
            y_pos = 300

        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(midbottom=(randint(900, 1100), y_pos))

    def animation_state(self):
        self.animation_index += 0.1
        if self.animation_index >= len(self.frames):
            self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def update(self):
        self.animation_state()
        self.rect.x -= 6
        self.destroy()

    def destroy(self):
        if self.rect.x <= -100:
            self.kill()

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        coin_image = pygame.image.load('graphics/coin/coin.png').convert_alpha()
        self.image = coin_image
        self.rect = self.image.get_rect(midbottom=(randint(900, 1100), 170))

    def update(self):
        self.rect.x -= int(obstacle_speed)
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

def read_high_score():
    try:
        with open('bestscore/score.txt', 'r') as file:
            content = file.read()
            if content:
                high_score = int(content)
            else:
                high_score = 0
    except FileNotFoundError:
        high_score = 0
    return high_score

def save_high_score(score):
    with open('bestscore/score.txt', 'w') as file:
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
coin_sound = pygame.mixer.Sound('audio/coin.mp3')
endcount = 0

player = pygame.sprite.GroupSingle()
player.add(Player())

obstacle_group = pygame.sprite.Group()

coin_group = pygame.sprite.Group()  # 코인 그룹 생성

coin_timer = pygame.USEREVENT + 2
pygame.time.set_timer(coin_timer, 5000)  # 5초마다 코인 생성

sky_surface = pygame.image.load('graphics/Background/Sky.png').convert()
ground_surface = pygame.image.load('graphics/Background/ground.png').convert()

player_stand = pygame.image.load('graphics/player/player_stand.png').convert_alpha()
player_stand = pygame.transform.rotozoom(player_stand, 0, 2)
player_stand_rect = player_stand.get_rect(center=(400, 200))

game_name = test_font.render('Mario Runner', False, (111, 196, 169))
game_name_rect = game_name.get_rect(center=(400, 80))

game_message = test_font.render('Press LSHIFT to sit', False, (240, 230, 140))
game_message_rect = game_message.get_rect(center=(400, 330))

obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1500)

obstacle_speed = 6
groundx = 0

high_score = read_high_score()
high_score_text = test_font.render(f'Best Score: {high_score}', False, (111, 196, 169))
high_score_rect = high_score_text.get_rect(center=(400, 70))

total_score = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if game_active:
            if event.type == obstacle_timer:
                obstacle_group.add(Obstacle(choice(['fly', 'snail', 'snail', 'snail'])))
                obstacle_speed += 0.3
            if event.type == coin_timer:
                coin_group.add(Coin())
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RSHIFT:
                if endcount == 1:
                    game_active = False
                    endcount = 0
                    score = 0
                    obstacle_group.empty()
                    coin_group.empty()
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
        screen.blit(ground_surface, (groundx, 300))
        screen.blit(ground_surface, (groundx + 800, 300))

        groundx -= int(obstacle_speed)

        if groundx <= -800:
            groundx = 0

        current_time = int(pygame.time.get_ticks() / 1000) - start_time  # 현재 시간 계산
        total_score = score + current_time  # 코인 점수와 현재 시간을 합한 점수

        # "Score"와 총 점수 표시
        score_text = test_font.render(f'Score: {total_score}', False, (64, 64, 64))
        score_text_rect = score_text.get_rect(center=(400, 40))
        screen.blit(score_text, score_text_rect)

        player.draw(screen)
        player.update()

        for obstacle in obstacle_group:
            obstacle.rect.x -= int(obstacle_speed)

        obstacle_group.draw(screen)
        obstacle_group.update()

        for coin in coin_group:
            coin.rect.x -= int(obstacle_speed)

        coin_group.draw(screen)
        coin_group.update()

        game_active = collision_sprite()
        
        # 코인과 플레이어의 충돌 처리
        coin_collisions = pygame.sprite.spritecollide(player.sprite, coin_group, True)
        if coin_collisions:
            score += 5
            coin_sound.play()

    else:
        screen.fill((94, 129, 162))
        screen.blit(player_stand, player_stand_rect)

        # "Your score"와 총 점수 표시
        score_message = test_font.render(f'Your score: {total_score}', False, (111, 196, 169))
        score_message_rect = score_message.get_rect(center=(400, 370))
        screen.blit(score_message, score_message_rect)

        # 최고 점수 표시
        high_score_text = test_font.render(f'Best Score: {high_score}', False, (111, 196, 169))
        high_score_rect = high_score_text.get_rect(center=(400, 70))
        screen.blit(high_score_text, high_score_rect)

        if total_score == 0:
            screen.blit(game_message, game_message_rect)
        else:
            bg_music.stop()
            if endcount == 0:
                game_over_sound.play()
                endcount = 1

        if total_score > high_score:
            high_score = total_score
            save_high_score(high_score)

    pygame.display.update()
    clock.tick(60)
