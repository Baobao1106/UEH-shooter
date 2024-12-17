import pygame
import os
import time
import random
import pygame, sys
from button import Button

pygame.init()

pygame.font.init()

WIDTH, HEIGHT = 1280, 720
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("UEH Space shooter")

# Load images
red_enemy = pygame.image.load(os.path.join("images", "virus.png"))
yellow_enemy = pygame.image.load(os.path.join("images", "virus (1).png"))
purple_enemy = pygame.image.load(os.path.join("images", "virus (2).png"))
green_enemy = pygame.image.load(os.path.join("images", "virus (3).png"))
pink_enemy = pygame.image.load(os.path.join("images", "virus (4).png"))

# player player
plane_main = pygame.image.load(os.path.join("images", "main player (3).png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("images", "Red laser.png"))
BLUE_LASER = pygame.image.load(os.path.join("images", "Blue laser.png"))
YELLOW_LASER = pygame.image.load(os.path.join("images", "Yellow laser.png"))
PURPLE_LASER = pygame.image.load(os.path.join("images", "Purple laser.png"))
PINK_LASER = pygame.image.load(os.path.join("images", "Pink laser.png"))
GREEN_LASER = pygame.image.load(os.path.join("images", "Green laser.png"))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
    
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.x += vel

    def off_screen(self, width):
        return not(self.x <= width and self.x >= 0)
    
    def collision(self, obj):
        return collide(self, obj)
    

class ship:

    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None 
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldonw()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(WIDTH):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)


    def cooldonw(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 30, self.y - 70, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
    
    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()

        
class Player(ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = plane_main
        self.laser_img = BLUE_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldonw()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(WIDTH):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x - 20 , self.y, 10, self.ship_img.get_height()))
        pygame.draw.rect(window, (0, 255, 0), (self.x - 20, self.y, 10, self.ship_img.get_height() * (self.health / self.max_health)))

class Enemy(ship):
    COLOR_MAP = {
                "red": (red_enemy, RED_LASER),
                "yellow": (yellow_enemy, YELLOW_LASER),
                "purple": (purple_enemy, PURPLE_LASER),
                "pink": (pink_enemy, PINK_LASER),
                "green": (green_enemy, GREEN_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.x -= vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-60, self.y-25, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
    
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 30)
    lost_font = pygame.font.SysFont("comicsans", 60)
    win_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 3
    enemy_vel = 1

    player_vel = 5
    laser_vel = 5

    player = Player(50, 300)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    win = False
    win_count = 0

    def redraw_window():
        WIN.blit(BG, (0, 0))
        # draw text 
        level_label = main_font.render(f"Level: {level}", 1, (0,0,0))
        lives_label = main_font.render(f"Lives: {lives}", 1, (0,0,0))
        
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(lives_label, (10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("Game Over!!!", 1, (255,255,255))
            lost_label1 = lost_font.render("Press Enter to play again or Esc to Quit", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 250))
            WIN.blit(lost_label1, (WIDTH/2 - lost_label1.get_width()/2, 350))

        if win:
            win_label = win_font.render("You Win!!!", 1, (255,255,255))
            WIN.blit(win_label, (WIDTH/2 - win_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            redraw_window()  # Giữ nguyên nền trò chơi và thông báo "Game Over!!!"

            # **Dừng vòng lặp trò chơi và chờ người chơi bấm Enter hoặc Esc**
            waiting_for_input = True
            while waiting_for_input:
            # Xử lý sự kiện bàn phím khi thua
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:  # Bấm Enter để chơi lại
                            main()  # Gọi lại hàm main để bắt đầu trò chơi mới
                        if event.key == pygame.K_ESCAPE:  # Bấm Esc để thoát
                            pygame.quit()
                            sys.exit()

        if level >= 3:
            win = True
            win_count += 1

        if win:
            redraw_window()  # Giữ nguyên nền trò chơi và thông báo "You Win!!!"

            if win_count > FPS*3:
                run = False
                global BG
                BG = pygame.transform.scale(pygame.image.load("images/pixel-desert-landscape-8-bit-game-level-background-vector.png"), (WIDTH, HEIGHT))
                main_menu()
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 2
            for i in range(wave_length):
                enemy = Enemy(random.randrange(1200, 1800), random.randrange(50, HEIGHT-200), random.choice(["red", "yellow", "purple", "pink", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: #right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(-laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)

            if enemy.x + enemy.get_width() < 0:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(laser_vel, enemies)

SCREEN = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Menu")

BG = pygame.image.load("images/pixel-desert-landscape-8-bit-game-level-background-vector.png")

def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("images/font.ttf", size)

def play():
    global BG # cho phép thay đổi biến BG

    # chuyển nền trò chơi
    BG = pygame.transform.scale(pygame.image.load("images/BackGround (2).jpg"), (WIDTH, HEIGHT))

    main()

def main_menu():
    while True:
        SCREEN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

        PLAY_BUTTON = Button(image=pygame.image.load("images/Play Rect.png"), pos=(640, 350), 
                            text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("images/Quit Rect.png"), pos=(640, 550), 
                            text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

main_menu()
