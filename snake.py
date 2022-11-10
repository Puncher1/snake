import json
import random
import sys
import time

import pygame


# Window init
pygame.init()

COLUMNS, ROWS, SIZE = 30, 30, 15
window = pygame.display.set_mode((COLUMNS*SIZE, ROWS*SIZE))
pygame.display.set_caption("Snake")

IMAGES_BASE = "./utils/images"
FONT_BASE = "./utils"
JSON_BASE = "./utils"

FONT = "game_over.ttf"
SCORE_JSON = "score.json"


class MouseClickEnum:
    LEFT_CLICK = 1
    MIDDLE_CLICK = 2
    RIGHT_CLICK = 3
    SCROLL_UP = 4
    SCROLL_DOWN = 5


class ScreenTypeEnum:
    HOME = 0
    SNAKE = 1
    PAUSE = 2
    PAUSE_COUNTDOWN = 3
    GAME_OVER = 4


class Button:

    def __init__(self, x, y, image):
        self.image = image
        self.x = x
        self.y = y


    def draw(self):
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

        window.blit(self.image, (self.rect.x, self.rect.y))


class Snake:

    def __init__(self):

        # *** Main Loop ***
        self.input_blocked = False
        self.delay_cyc = 100    # in ms
        self.delay_pv = 0       # in ms

        self.current_screen = ScreenTypeEnum.HOME


        # *** Snake init ***
        self.body = [(1, 1)]
        self.direction_grid = (1, 0)
        self.next_move = (1, 0)
        self.food = self.random_pos()
        self.last_part_pos = None


        # *** Images ***

        # Start button images
        self.start_img = pygame.image.load(f"{IMAGES_BASE}/start_btn_pixelart.png").convert()
        self.start_clicked_img = pygame.image.load(f"{IMAGES_BASE}/start_btnclicked_pixelart.png").convert()
        self.start_hovered_img = pygame.image.load(f"{IMAGES_BASE}/start_btnhovered_pixelart.png").convert()

        # Resume button images
        self.resume_img = pygame.image.load(f"{IMAGES_BASE}/resume_btn_pixelart.png").convert()
        self.resume_clicked_img = pygame.image.load(f"{IMAGES_BASE}/resume_btnclicked_pixelart.png").convert()
        self.resume_hovered_img = pygame.image.load(f"{IMAGES_BASE}/resume_btnhovered_pixelart.png").convert()

        # Home button images
        self.home_img = pygame.image.load(f"{IMAGES_BASE}/home_btn_pixelart.png").convert()
        self.home_clicked_img = pygame.image.load(f"{IMAGES_BASE}/home_btnclicked_pixelart.png").convert()
        self.home_hovered_img = pygame.image.load(f"{IMAGES_BASE}/home_btnhovered_pixelart.png").convert()

        # Restart button images
        self.restart_img = pygame.image.load(f"{IMAGES_BASE}/restart_btn_pixelart.png").convert()
        self.restart_clicked_img = pygame.image.load(f"{IMAGES_BASE}/restart_btnclicked_pixelart.png").convert()
        self.restart_hovered_img = pygame.image.load(f"{IMAGES_BASE}/restart_btnhovered_pixelart.png").convert()
        
        # Exit button images
        self.exit_img = pygame.image.load(f"{IMAGES_BASE}/exit_btn_pixelart.png").convert()
        self.exit_clicked_img = pygame.image.load(f"{IMAGES_BASE}/exit_btnclicked_pixelart.png").convert()
        self.exit_hovered_img = pygame.image.load(f"{IMAGES_BASE}/exit_btnhovered_pixelart.png").convert()


        # *** Buttons ***

        # Start button
        self.start_btn = Button((COLUMNS * SIZE / 2) - 100, (ROWS * SIZE / 2) + 100, self.start_img)
        self.start_btn_clicked = False

        # Resume button
        self.resume_btn = Button((COLUMNS * SIZE / 2) - 100, (ROWS * SIZE / 2) + 100, self.resume_img)
        self.resume_btn_clicked = False

        # Home button
        self.home_btn = Button((COLUMNS * SIZE / 2) + 100, (ROWS * SIZE / 2) + 100, self.home_img)
        self.home_btn_clicked = False

        # Restart button
        self.restart_btn = Button((COLUMNS * SIZE / 2) - 100, (ROWS * SIZE / 2) + 100, self.restart_img)
        self.restart_btn_clicked = False

        # Exit button
        self.exit_btn = Button((COLUMNS * SIZE / 2) + 100, (ROWS * SIZE / 2) + 100, self.exit_img)
        self.exit_btn_clicked = False


        # *** Score ***
        self.new_high_score = False
        self.hs_show = True
        self.hs_blink_cyc = 400    # in ms
        self.hs_blink_pv = 0       # in ms

        self.current_score = 0


        # *** Pause Countdown ***
        self.pause_delay_cyc = 1000     # in ms
        self.pause_delay_pv = 0         # in ms
        self.pause_count = 3
        self.is_first_pause_count_run = True

    def random_pos(self):
        while True:
            pos = (random.randrange(COLUMNS), random.randrange(ROWS))
            if pos not in self.body:
                break

        return pos

    def home_screen(self):
        font_title = pygame.font.Font(f"{FONT_BASE}/{FONT}", 150)
        title = font_title.render("Snake", True, (255, 255, 255))
        title_rect = title.get_rect()
        title_rect.center = ((COLUMNS*SIZE/2), (ROWS*SIZE/2)-50)

        with open(f"{JSON_BASE}/{SCORE_JSON}", "r") as fscore:
            data = json.load(fscore)
        try:
            json_high_score = data["high_score"]
        except KeyError:
            json_high_score = 0

        font_high_score = pygame.font.Font(f"{FONT_BASE}/{FONT}", 70)
        high_score = font_high_score.render(f"High Score: {json_high_score}", True, (224, 185, 92))
        high_score_rect = high_score.get_rect()
        high_score_rect.center = ((COLUMNS*SIZE/2), (ROWS*SIZE/2)+15)

        window.fill((0, 0, 0))
        window.blit(title, title_rect)

        if self.new_high_score:
            if self.hs_blink_pv >= self.hs_blink_cyc:
                self.hs_blink_pv = 0
                self.hs_show = not self.hs_show
            else:
                self.hs_blink_pv += 1

        if self.hs_show:
            window.blit(high_score, high_score_rect)

        self.exit_btn.draw()
        self.start_btn.draw()

        pygame.display.update()

    def home_btn_handler(self, event):
        mouse_pos = pygame.mouse.get_pos()

        # Mouse button clicked
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.exit_btn.rect.collidepoint(mouse_pos):
                # Update exit button with clicked img
                self.exit_btn.image = self.exit_clicked_img
                self.exit_btn.y += 1

                self.exit_btn_clicked = True

            elif self.start_btn.rect.collidepoint(mouse_pos):
                # Update start button with clicked img
                self.start_btn.image = self.start_clicked_img
                self.start_btn.y += 1

                self.start_btn_clicked = True

        # Mouse button released
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.exit_btn_clicked:
                self.exit_btn_clicked = False

                self.exit_btn.image = self.exit_img
                self.exit_btn.y -= 1

                sys.exit()

            elif self.start_btn_clicked:
                self.start_btn_clicked = False

                self.start_btn.image = self.start_img
                self.start_btn.y -= 1

                self.snake_reset()
                self.current_screen = ScreenTypeEnum.SNAKE

    def pause_screen(self):
        font_title = pygame.font.Font(f"{FONT_BASE}/{FONT}", 150)
        title = font_title.render("Pause", True, (255, 255, 255))
        title_rect = title.get_rect()
        title_rect.center = ((COLUMNS * SIZE / 2), (ROWS * SIZE / 2) - 50)

        window.fill((0, 0, 0))
        window.blit(title, title_rect)
        self.home_btn.draw()
        self.resume_btn.draw()

        pygame.display.update()

    def pause_btn_handler(self, event):
        mouse_pos = pygame.mouse.get_pos()

        # Mouse button clicked
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.home_btn.rect.collidepoint(mouse_pos):
                # Update home button with clicked img
                self.home_btn.image = self.home_clicked_img
                self.home_btn.y += 1

                self.home_btn_clicked = True

            elif self.resume_btn.rect.collidepoint(mouse_pos):
                # Update resume button with clicked img
                self.resume_btn.image = self.resume_clicked_img
                self.resume_btn.y += 1

                self.resume_btn_clicked = True

        # Mouse button released
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.home_btn_clicked:
                self.home_btn_clicked = False

                self.home_btn.image = self.home_img
                self.exit_btn.y -= 1

                self.current_screen = ScreenTypeEnum.HOME

            elif self.resume_btn_clicked:
                self.resume_btn_clicked = False

                self.resume_btn.image = self.resume_img
                self.resume_btn.y -= 1

                self.current_screen = ScreenTypeEnum.PAUSE_COUNTDOWN

    def pause_countdown_screen(self):
        font_countdown = pygame.font.Font(f"{FONT_BASE}/{FONT}", 150)
        countdown = font_countdown.render(f"{self.pause_count}", True, (255, 255, 255))
        countdown_rect = countdown.get_rect()
        countdown_rect.center = ((COLUMNS * SIZE / 2), (ROWS * SIZE / 2) - 50)

        if self.is_first_pause_count_run:
            self.is_first_pause_count_run = False
            self.snake_screen()
            window.blit(countdown, countdown_rect)
            pygame.display.update()

        if self.is_next_pause_count_due():
            self.pause_count -= 1

            countdown = font_countdown.render(f"{self.pause_count}", True, (255, 255, 255))

            self.snake_screen_draw()
            window.blit(countdown, countdown_rect)
            pygame.display.update()

        if self.pause_count == 0:
            self.is_first_pause_count_run = True
            self.pause_count = 3
            self.current_screen = ScreenTypeEnum.SNAKE

    def game_over_screen(self):
        font_title = pygame.font.Font(f"{FONT_BASE}/{FONT}", 150)
        title = font_title.render("Game Over!", True, (255, 255, 255))
        title_rect = title.get_rect()
        title_rect.center = ((COLUMNS*SIZE/2), (ROWS*SIZE/2)-50)

        with open(f"{JSON_BASE}/{SCORE_JSON}", "r") as fscore:
            data = json.load(fscore)
        try:
            json_last_score = data["last_score"]
        except KeyError:
            json_last_score = 0

        font_last_score = pygame.font.Font(f"{FONT_BASE}/{FONT}", 70)
        last_score = font_last_score.render(f"Score: {json_last_score}", True, (255, 255, 255))
        last_score_rect = last_score.get_rect()
        last_score_rect.center = ((COLUMNS * SIZE / 2), (ROWS * SIZE / 2) + 15)

        window.fill((0, 0, 0))
        window.blit(title, title_rect)
        window.blit(last_score, last_score_rect)

        self.home_btn.draw()
        self.restart_btn.draw()

        pygame.display.update()

    def game_over_btn_handler(self, event):
        mouse_pos = pygame.mouse.get_pos()

        # Mouse button clicked
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.home_btn.rect.collidepoint(mouse_pos):
                # Update home button with clicked img
                self.home_btn.image = self.home_clicked_img
                self.home_btn.y += 1

                self.home_btn_clicked = True

            elif self.restart_btn.rect.collidepoint(mouse_pos):
                # Update restart button with clicked img
                self.restart_btn.image = self.restart_clicked_img
                self.restart_btn.y += 1

                self.restart_btn_clicked = True

        # Mouse button released
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.home_btn_clicked:
                self.home_btn_clicked = False

                self.home_btn.image = self.home_img
                self.home_btn.y -= 1

                self.current_screen = ScreenTypeEnum.HOME

            elif self.restart_btn_clicked:
                self.restart_btn_clicked = False

                self.restart_btn.image = self.restart_img
                self.restart_btn.y -= 1

                self.snake_reset()
                self.current_screen = ScreenTypeEnum.SNAKE

    def snake_screen_draw(self):
        window.fill((0, 0, 0))
        pygame.draw.rect(window, (255, 0, 255), (self.food[0] * SIZE, self.food[1] * SIZE, SIZE, SIZE))

        for part in self.body:
            pygame.draw.rect(window, (0, 255, 00), (part[0] * SIZE, part[1] * SIZE, SIZE, SIZE))

    def snake_screen(self):
        self.snake_screen_draw()

        pygame.display.update()

    def snake_update_next_move(self, event):
        self.input_blocked = True

        if event.key == pygame.K_RIGHT and self.next_move != (-1, 0):
            self.next_move = (1, 0)
        elif event.key == pygame.K_LEFT and self.next_move != (1, 0):
            self.next_move = (-1, 0)
        elif event.key == pygame.K_UP and self.next_move != (0, 1):
            self.next_move = (0, -1)
        elif event.key == pygame.K_DOWN and self.next_move != (0, -1):
            self.next_move = (0, 1)
        else:
            self.input_blocked = False

    def snake_move(self):
        self.body.insert(0, (self.body[0][0] + self.next_move[0], self.body[0][1] + self.next_move[1]))
        self.last_part_pos = self.body[-1]
        del self.body[-1]

    def snake_grow(self):
        self.food = self.random_pos()
        self.body.append(self.last_part_pos)
        self.current_score += 1

    def snake_check_move(self):
        border_check = (self.body[0][0] >= COLUMNS or self.body[0][0] < 0) or (self.body[0][1] >= ROWS or self.body[0][1] < 0)
        eat_body_check = self.body[0] in [part for i, part in enumerate(self.body) if i != 0]

        check_list = [border_check, eat_body_check]
        is_check_true = False
        for check in check_list:
            if check:
                is_check_true = True
                break
        return is_check_true

    def snake_reset(self):
        self.body = [(1, 1)]
        self.direction_grid = (1, 0)
        self.next_move = (1, 0)
        self.food = self.random_pos()
        self.last_part_pos = None

    def save_score(self):
        with open(f"{JSON_BASE}/{SCORE_JSON}", "r") as fscore:
            data = json.load(fscore)

        data["last_score"] = self.current_score

        try:
            high_score = data["high_score"]
        except KeyError:
            data["high_score"] = self.current_score
            high_score = 0

        if self.current_score > high_score:
            data["high_score"] = self.current_score
            self.new_high_score = True
        else:
            self.new_high_score = False

        with open(f"{JSON_BASE}/{SCORE_JSON}", "w") as fscore:
            json.dump(data, fscore, sort_keys=True, indent=4)

        self.current_score = 0
        self.hs_show = True

    def is_next_pause_count_due(self):
        pygame.time.delay(1)

        if self.pause_delay_pv >= self.pause_delay_cyc:
            self.pause_delay_pv = 0
            return True
        else:
            self.pause_delay_pv += 1
            return False

    def is_next_snake_loop_due(self):
        pygame.time.delay(1)

        if self.delay_pv >= self.delay_cyc:
            self.delay_pv = 0
            return True
        else:
            self.delay_pv += 1
            return False

    def main_loop(self):
        while True:

            if self.current_screen == ScreenTypeEnum.HOME:
                self.home_screen()

            elif self.current_screen == ScreenTypeEnum.SNAKE:
                if self.is_next_snake_loop_due():
                    self.input_blocked = False

                    self.snake_move()

                    # Check if snake eats food
                    if self.body[0] == self.food:
                        self.snake_grow()

                    # Check snake movement
                    if self.snake_check_move():
                        self.current_screen = ScreenTypeEnum.GAME_OVER
                        self.save_score()
                        continue
                self.snake_screen()

            elif self.current_screen == ScreenTypeEnum.PAUSE:
                self.pause_screen()

            elif self.current_screen == ScreenTypeEnum.PAUSE_COUNTDOWN:
                self.pause_countdown_screen()

            elif self.current_screen == ScreenTypeEnum.GAME_OVER:
                self.game_over_screen()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if self.current_screen == ScreenTypeEnum.SNAKE:
                        if not self.input_blocked:
                            self.snake_update_next_move(event)

                        if event.key == pygame.K_ESCAPE:
                            self.current_screen = ScreenTypeEnum.PAUSE
                            continue

                    elif self.current_screen == ScreenTypeEnum.PAUSE:
                        if event.key == pygame.K_ESCAPE:
                            self.current_screen = ScreenTypeEnum.PAUSE_COUNTDOWN
                            continue

                if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
                    if event.button == MouseClickEnum.LEFT_CLICK:
                        if self.current_screen == ScreenTypeEnum.HOME:
                            self.home_btn_handler(event)

                        elif self.current_screen == ScreenTypeEnum.GAME_OVER:
                            self.game_over_btn_handler(event)

                        elif self.current_screen == ScreenTypeEnum.PAUSE:
                            self.pause_btn_handler(event)

                elif event.type == pygame.MOUSEMOTION:
                    mouse_pos = pygame.mouse.get_pos()

                    if self.current_screen == ScreenTypeEnum.HOME:
                        if not self.start_btn.image == self.start_clicked_img:
                            if self.start_btn.rect.collidepoint(mouse_pos):
                                self.start_btn.image = self.start_hovered_img
                            else:
                                self.start_btn.image = self.start_img

                        if not self.exit_btn.image == self.exit_clicked_img:
                            if self.exit_btn.rect.collidepoint(mouse_pos):
                                self.exit_btn.image = self.exit_hovered_img
                            else:
                                self.exit_btn.image = self.exit_img

                    elif self.current_screen == ScreenTypeEnum.PAUSE:
                        if not self.resume_btn.image == self.resume_clicked_img:
                            if self.resume_btn.rect.collidepoint(mouse_pos):
                                self.resume_btn.image = self.resume_hovered_img
                            else:
                                self.resume_btn.image = self.resume_img

                        if not self.home_btn.image == self.home_clicked_img:
                            if self.home_btn.rect.collidepoint(mouse_pos):
                                self.home_btn.image = self.home_hovered_img
                            else:
                                self.home_btn.image = self.home_img

                    elif self.current_screen == ScreenTypeEnum.GAME_OVER:
                        if not self.restart_btn.image == self.restart_clicked_img:
                            if self.restart_btn.rect.collidepoint(mouse_pos):
                                self.restart_btn.image = self.restart_hovered_img
                            else:
                                self.restart_btn.image = self.restart_img

                        if not self.home_btn.image == self.home_clicked_img:
                            if self.home_btn.rect.collidepoint(mouse_pos):
                                self.home_btn.image = self.home_hovered_img
                            else:
                                self.home_btn.image = self.home_img


snake_game = Snake()
if __name__ == "__main__":
    snake_game.main_loop()
