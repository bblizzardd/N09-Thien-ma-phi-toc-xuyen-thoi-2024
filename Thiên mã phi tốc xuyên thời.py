import pygame
from random import randint
import os
import sys

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 775
FPS = 60

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Thiên mã phi tốc xuyên thời')
clock = pygame.time.Clock()

# Thư mục gốc chứa tài nguyên (hỗ trợ cả môi trường script thường và PyInstaller đóng gói)
if getattr(sys, 'frozen', False):
    if hasattr(sys, '_MEIPASS') and os.path.exists(os.path.join(sys._MEIPASS, 'WELCOME.png')):
        BASE_DIR = sys._MEIPASS
    else:
        BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Bảng màu sắc chuẩn
PINK = (255, 102, 153)
WHITE = (255, 255, 255)
GREY = (89, 89, 89)
BLACK = (0, 0, 0)
BLUE = (12, 192, 223)
YELLOW = (255, 222, 89)
GREEN = (126, 217, 87)
RED = (255, 49, 49)

PLAYER_COLORS = [BLUE, YELLOW, GREEN, RED]

# Phông chữ tái sử dụng (không khởi tạo lại ở mỗi frame)
font_large = pygame.font.SysFont('sans', 80)
font_score = pygame.font.SysFont('sans', 70)
font_text = pygame.font.SysFont('sans', 30)

# Trạng thái luồng game (State Machine)
STATE_MENU = 0
STATE_GAME = 1
STATE_INSTRUCTION = 2
STATE_GAME_OVER = 3

# Trạng thái lượt chơi trong game
PHASE_ROLL_DICE = 0
PHASE_DICE_SHOW = 1
PHASE_SELECT_PIECE = 2


def load_image(filename):
    """Tải hình ảnh an toàn và tối ưu định dạng pixel cho tốc độ render cao."""
    path = os.path.join(BASE_DIR, filename)
    if os.path.exists(path):
        try:
            return pygame.image.load(path).convert_alpha()
        except Exception:
            try:
                return pygame.image.load(path).convert()
            except Exception:
                pass
    # Trả về Surface dự phòng nếu không tìm thấy file để tránh crash
    surf = pygame.Surface((50, 50), pygame.SRCALPHA)
    surf.fill((200, 200, 200, 180))
    return surf

def load_sound(filename):
    """Tải hiệu ứng âm thanh an toàn."""
    path = os.path.join(BASE_DIR, filename)
    if os.path.exists(path):
        try:
            return pygame.mixer.Sound(path)
        except Exception:
            return None
    return None

def play_music(filename, loop=-1):
    """Phát nhạc nền an toàn."""
    path = os.path.join(BASE_DIR, filename)
    if os.path.exists(path):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(loop)
        except Exception:
            pass

# Load các hình ảnh giao diện & nút bấm
image_menu = load_image("WELCOME.png")
image_end_game_menu = load_image("END_GAME_menu.png")
image_back_white = load_image("RETURN_1.png")
image_back = load_image("RETURN_2.png")
image_instruc = load_image("INSTRUCTION.png")
image_background = load_image("IN GAME.png")

image_newgame = load_image("NEW GAME.png")
image_how_to_play = load_image("HOW TO PLAY.png")
image_quit = load_image("QUIT.png")
image_newgame_white = load_image("NEW GAME_2.png")
image_how_to_play_white = load_image("HOW TO PLAY_2.png")
image_quit_white = load_image("QUIT_2.png")
image_end_game = load_image("END GAME_2.png")
image_end_game_white = load_image("END GAME.png")

image_turn = [
    load_image("BLUE TURN.png"),
    load_image("YELLOW TURN.png"),
    load_image("GREEN TURN.png"),
    load_image("RED TURN.png")
]

image_seahorse = [
    load_image("SEAHORSE_BLUE.png"),
    load_image("SEAHORSE_YELLOW.png"),
    load_image("SEAHORSE_GREEN.png"),
    load_image("SEAHORSE_RED.png")
]

image_seahorse_55X55 = [
    load_image("SEAHORSE_BLUE_55X55.png"),
    load_image("SEAHORSE_YELLOW_55X55.png"),
    load_image("SEAHORSE_GREEN_55X55.png"),
    load_image("SEAHORSE_RED_55X55.png")
]

image_dice = load_image("dice.png")
image_dice_1_1x = load_image("dice_1.1x.png")

image_win = [
    load_image("BLUE.png"),
    load_image("YELLOW.png"),
    load_image("GREEN.png"),
    load_image("RED.png")
]

# Load âm thanh
sound_pickleball = load_sound("Pickleball.wav")
sound_button1 = load_sound("BUTTON.wav")
sound_button2 = load_sound("CARTOON_BUTTON.wav")

def play_sfx(sound):
    if sound:
        sound.play()


# TỌA ĐỘ BÀN CỜ

BOARD_COORDS = {
    # Đường đi chính (48 ô: 0 đến 47)
    0: (245, 20),   1: (245, 60),   2: (245, 110),  3: (245, 155),
    4: (245, 200),  5: (245, 245),  6: (200, 245),  7: (155, 245),
    8: (110, 245),  9: (65, 245),   10: (20, 245),  11: (20, 345),
    12: (20, 425),  13: (65, 425),  14: (110, 425), 15: (155, 425),
    16: (200, 425), 17: (245, 425), 18: (245, 470), 19: (245, 515),
    20: (245, 560), 21: (245, 605), 22: (245, 650), 23: (340, 650),
    24: (420, 650), 25: (420, 605), 26: (420, 560), 27: (420, 515),
    28: (420, 470), 29: (420, 425), 30: (470, 425), 31: (515, 425),
    32: (560, 425), 33: (605, 425), 34: (650, 425), 35: (650, 340),
    36: (655, 245), 37: (610, 245), 38: (565, 245), 39: (520, 245),
    40: (475, 245), 41: (425, 245), 42: (425, 200), 43: (425, 155),
    44: (425, 112), 45: (425, 60),  46: (425, 20),  47: (340, 20),

    # Chuồng Blue (100 - 106)
    100: (340, 20), 101: (335, 65),  102: (335, 105),
    103: (335, 145), 104: (335, 185), 105: (335, 225), 106: (335, 265),

    # Chuồng Yellow (200 - 206)
    200: (20, 345), 201: (70, 340),  202: (110, 340),
    203: (150, 340), 204: (190, 340), 205: (230, 340), 206: (270, 340),

    # Chuồng Green (300 - 306)
    300: (340, 650), 301: (335, 605), 302: (335, 565),
    303: (335, 525), 304: (335, 485), 305: (335, 445), 306: (335, 405),

    # Chuồng Red (400 - 406)
    400: (655, 340), 401: (600, 340), 402: (560, 340),
    403: (520, 340), 404: (480, 340), 405: (440, 340), 406: (400, 340)
}

# Tọa độ xuất phát trong chuồng (chuẩn hóa 4 đội)
START_COORDS = [
    # Blue (0-3)
    (70, 60),   (130, 60),  (70, 120),  (130, 120),
    # Yellow (4-7)
    (70, 530),  (130, 530), (70, 590),  (130, 590),
    # Green (8-11)
    (540, 530), (600, 530), (540, 590), (600, 590),
    # Red (12-15)
    (540, 60),  (600, 60),  (540, 120), (600, 120)
]


class Seahorse:
    __slots__ = ('idx', 'team', 'start_x', 'start_y', 'x', 'y', 'pos', 'cage', 'finish', 'finish_check')
    def __init__(self, idx, start_x, start_y):
        self.idx = idx
        self.team = idx // 4
        self.start_x = start_x
        self.start_y = start_y
        self.x = start_x
        self.y = start_y
        self.pos = -1
        self.cage = 0
        self.finish = 0
        self.finish_check = 0

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.pos = -1
        self.cage = 0
        self.finish = 0
        self.finish_check = 0


# QUẢN LÝ TRẠNG THÁI VÀ LOGIC GAME

class LudoGame:
    def __init__(self):
        self.seahorses = [Seahorse(i, START_COORDS[i][0], START_COORDS[i][1]) for i in range(16)]
        self.place = [0] * 500
        self.place_color = [-1] * 500
        self.chess_num = [0] * 4
        self.points = [0] * 16
        self.team_points = [0, 0, 0, 0]
        self.max_pos = [47 if i < 4 else 100 for i in range(16)]
        self.turn = 0
        self.dice_num = 0
        self.phase = PHASE_ROLL_DICE
        self.dice_show_start_time = 0

    def reset(self):
        """Khởi động lại toàn bộ bàn cờ về trạng thái ban đầu."""
        for h in self.seahorses:
            h.reset()
        self.place = [0] * 500
        self.place_color = [-1] * 500
        self.chess_num = [0] * 4
        self.points = [0] * 16
        self.team_points = [0, 0, 0, 0]
        self.max_pos = [47 if i < 4 else 100 for i in range(16)]
        self.turn = 0
        self.dice_num = 0
        self.phase = PHASE_ROLL_DICE
        self.dice_show_start_time = 0

    def calculate_track_position(self, i, current_pos, dice):
        """Tính toán ô đến trên đường chạy chính theo quy tắc cờ cá ngựa gốc."""
        pos = current_pos
        if 0 <= i <= 3:
            if (0 <= 12 - pos <= dice) or (0 <= 24 - pos <= dice) or (0 <= 36 - pos <= dice):
                pos += 1
        elif 4 <= i <= 7:
            if (0 <= 48 - pos <= dice) or (0 <= 24 - pos <= dice) or (0 <= 36 - pos <= dice):
                pos += 1
        elif 8 <= i <= 11:
            if (0 <= 12 - pos <= dice) or (0 <= 48 - pos <= dice) or (0 <= 36 - pos <= dice):
                pos += 1
        elif 12 <= i <= 15:
            if (0 <= 12 - pos <= dice) or (0 <= 24 - pos <= dice) or (0 <= 48 - pos <= dice):
                pos += 1

        return (pos + dice) % 48

    def is_turn_possible(self, i, dice):
        """Kiểm tra quân cờ i có thể di chuyển hợp lệ với số nút dice hay không."""
        h = self.seahorses[i]
        team = h.team

        # Quân đang ở trong chuồng
        if h.cage == 0:
            start_tile = team * 12
            if dice == 6 and self.place[start_tile] == 0 and h.pos == -1:
                return True
            return False

        # Quân đã ra ngoài bàn cờ
        if h.cage != 0:
            if h.pos + dice <= self.max_pos[i]:
                target_check = h.pos + dice
                if self.place[target_check] == 1:
                    if self.place_color[target_check] != team:
                        return True
                else:
                    return True

            if h.finish == 1:
                base = 100 * (team + 1)
                if self.place[base + dice] != 1:
                    return True
                if h.finish_check == 1:
                    if self.place[h.pos + dice] != 1:
                        if dice > (h.pos - base) and (h.pos + dice <= 6 + base):
                            return True

        return False

    def check_any_move_possible(self):
        """Kiểm tra đội hiện tại có bất kỳ quân nào đi được không."""
        start_idx = self.turn * 4
        for k in range(start_idx, start_idx + 4):
            if self.is_turn_possible(k, self.dice_num):
                return True
        return False

    def roll_dice(self):
        """Đổ xúc xắc và chuyển trạng thái hiển thị."""
        self.dice_num = randint(1, 6)
        self.phase = PHASE_DICE_SHOW
        self.dice_show_start_time = pygame.time.get_ticks()

    def update_dice_phase(self):
        """Xử lý sau khi hiển thị xúc xắc đủ thời gian mà không gây lag luồng game."""
        if self.phase == PHASE_DICE_SHOW:
            current_time = pygame.time.get_ticks()
            if current_time - self.dice_show_start_time >= 600:
                # Nếu chưa có quân nào xuất chuồng và không đổ được 6 -> mất lượt
                if self.chess_num[self.turn] == 0 and self.dice_num != 6:
                    self.turn = (self.turn + 1) % 4
                    self.dice_num = 0
                    self.phase = PHASE_ROLL_DICE
                    return

                # Nếu không có quân nào đi được -> mất lượt
                if not self.check_any_move_possible():
                    self.turn = (self.turn + 1) % 4
                    self.dice_num = 0
                    self.phase = PHASE_ROLL_DICE
                    return

                # Có nước đi hợp lệ -> chờ người chơi bấm chọn quân
                self.phase = PHASE_SELECT_PIECE

    def move_piece(self, i):
        """Thực hiện di chuyển quân cờ i theo luật cờ cá ngựa."""
        h = self.seahorses[i]
        team = h.team
        prev_pos = h.pos

        # 1. Xuất chuồng khi đổ được 6
        if self.dice_num == 6 and h.cage == 0 and h.pos == -1:
            start_tile = team * 12
            if self.place[start_tile] == 0:
                h.x, h.y = BOARD_COORDS[start_tile]
                self.chess_num[team] += 1
                h.pos = start_tile
                self.place[start_tile] = 1
                self.place_color[start_tile] = team
                h.cage = 1
                self.dice_num = 0
                self.phase = PHASE_ROLL_DICE
                # Đổ được 6 được đi tiếp
                return True
            return False

        if h.cage == 0:
            return False

        # 2. Di chuyển quân đang trên bàn hoặc đang về chuồng
        base = 100 * (team + 1)
        if h.finish == 1:
            if h.finish_check == 1:
                if self.dice_num == h.pos - base + 1:
                    h.pos = base + self.dice_num
            else:
                h.pos = base + self.dice_num
            self.place[h.pos] = 1

        if h.pos > base:
            h.finish_check = 1
        elif h.finish == 0:
            if h.cage == 1:
                if h.pos + self.dice_num <= self.max_pos[i]:
                    self.place[prev_pos] = 0
                    new_pos = self.calculate_track_position(i, h.pos, self.dice_num)
                    if (h.pos + self.dice_num) > 47 and i >= 4:
                        self.max_pos[i] = (team * 12) - 1
                    h.pos = new_pos

        # Kiểm tra trùng ô với quân cùng đội
        if self.place[h.pos] == 1 and self.place_color[h.pos] == team:
            h.pos = prev_pos
            self.place[prev_pos] = 1
            return False

        # Kiểm tra giới hạn chuồng
        if h.pos - base > self.dice_num:
            return False

        # 3. Đá quân địch (nếu ô đến có quân đối phương)
        if self.place[h.pos] == 1 and self.place_color[h.pos] != team:
            for j in range(16):
                if self.seahorses[j].pos == h.pos and j != i:
                    enemy_h = self.seahorses[j]
                    enemy_team = enemy_h.team
                    # Trừ điểm quân bị đá
                    self.team_points[enemy_team] -= self.points[j]
                    self.points[j] = 0
                    enemy_h.pos = -1
                    enemy_h.cage = 0
                    enemy_h.finish = 0
                    enemy_h.finish_check = 0
                    self.max_pos[j] = 47 if enemy_team == 0 else 100
                    enemy_h.x = enemy_h.start_x
                    enemy_h.y = enemy_h.start_y
                    self.chess_num[enemy_team] -= 1
                    self.place[h.pos] = 0
                    break

        # 4. Cập nhật vị trí đích và điểm số
        if h.pos == self.max_pos[i]:
            h.finish = 1

        if h.pos in BOARD_COORDS:
            h.x, h.y = BOARD_COORDS[h.pos]
            self.place[h.pos] = 1
            if prev_pos != -1:
                self.place[prev_pos] = 0
            self.place_color[h.pos] = team

            if h.pos >= base + 1:
                self.points[i] = 44 + self.dice_num * self.dice_num
            else:
                self.points[i] += self.dice_num

            self.team_points[team] = sum(self.points[team * 4 : (team + 1) * 4])

            # Chuyển lượt (đổ được 6 được giữ lượt)
            if self.dice_num != 6:
                self.turn = (self.turn + 1) % 4
            self.dice_num = 0
            self.phase = PHASE_ROLL_DICE
            return True

        return False

# ==============================================================================
# HÀM XỬ LÝ CLICK QUÂN CỜ (ĐÃ GỘP 4 HÀM TRÙNG LẶP THÀNH 1)
# ==============================================================================
def get_clicked_seahorse(team, mx, my, seahorses):
    """Tìm quân cờ của đội hiện tại được người chơi click chuột."""
    start_idx = team * 4
    for i in range(start_idx, start_idx + 4):
        h = seahorses[i]
        if (h.x - 10 <= mx <= h.x + 60) and (h.y - 10 <= my <= h.y + 60):
            return i
    return -1

# ==============================================================================
# CÁC MÀN HÌNH GIAO DIỆN (STATE VIEWS)
# ==============================================================================
def draw_menu(screen, mx, my):
    """Vẽ màn hình Menu chính."""
    screen.blit(image_menu, (0, 0))

    # Nút New Game
    if 360 < mx < 650 and 490 < my < 550:
        screen.blit(image_newgame, (350, 495))
    else:
        screen.blit(image_newgame_white, (350, 495))

    # Nút How to Play
    if 360 < mx < 650 and 560 < my < 620:
        screen.blit(image_how_to_play, (350, 565))
    else:
        screen.blit(image_how_to_play_white, (350, 565))

    # Nút Quit
    if 360 < mx < 650 and 630 < my < 690:
        screen.blit(image_quit, (350, 635))
    else:
        screen.blit(image_quit_white, (350, 635))

def draw_instruction(screen, mx, my):
    """Vẽ màn hình Hướng dẫn."""
    screen.blit(image_instruc, (0, 0))
    if 660 < mx < 920 and 640 < my < 690:
        screen.blit(image_back, (660, 645))
    else:
        screen.blit(image_back_white, (660, 645))

def draw_game(screen, mx, my, game):
    """Vẽ màn hình Bàn cờ chơi game."""
    screen.blit(image_background, (0, 0))

    # Nút xúc xắc & hiệu ứng hover
    if (765 < mx < 965) and (515 < my < 680):
        screen.blit(image_dice_1_1x, (705, 465))
    else:
        screen.blit(image_dice, (765, 515))

    # Nút End Game
    if (705 < mx < 1000) and (720 < my < 770):
        screen.blit(image_end_game, (700, 720))
    else:
        screen.blit(image_end_game_white, (700, 720))

    # Vẽ 16 quân cờ (phóng to khi hover)
    for chess_number in range(16):
        h = game.seahorses[chess_number]
        team_idx = chess_number // 4
        if h.x <= mx <= h.x + 50 and h.y <= my <= h.y + 50:
            screen.blit(image_seahorse_55X55[team_idx], (h.x - 5, h.y - 5))
        else:
            screen.blit(image_seahorse[team_idx], (h.x, h.y))

    # Hiển thị điểm số 4 đội
    score_positions = [(880, 195), (880, 265), (880, 335), (880, 410)]
    for idx, (sx, sy) in enumerate(score_positions):
        text_surface = font_score.render(str(game.team_points[idx]), True, WHITE)
        screen.blit(text_surface, (sx, sy))

    # Hiển thị lượt chơi hiện tại
    screen.blit(image_turn[game.turn], (720, 25))

    # Hiển thị số nút xúc xắc vừa đổ
    if game.phase in (PHASE_DICE_SHOW, PHASE_SELECT_PIECE) and game.dice_num > 0:
        dice_text = font_score.render(str(game.dice_num), True, BLACK)
        screen.blit(dice_text, (345, 325))

def draw_game_over(screen, game):
    """Vẽ màn hình Kết thúc trận đấu."""
    screen.blit(image_end_game_menu, (0, 0))
    max_value = max(game.team_points)
    winner_idx = game.team_points.index(max_value)

    screen.blit(image_win[winner_idx], (500, 230))
    point_result_text = font_large.render(str(max_value), True, PLAYER_COLORS[winner_idx])
    screen.blit(point_result_text, (570, 310))

# ==============================================================================
# VÒNG LẶP CHÍNH (MAIN GAME LOOP - STATE MACHINE KHÔNG ĐỆ QUY)
# ==============================================================================
def main():
    current_state = STATE_MENU
    running = True
    game = LudoGame()

    # Bắt đầu phát nhạc menu
    play_music("Pickleball.wav", -1)

    while running:
        mx, my = pygame.mouse.get_pos()

        # ----------------------------------------------------------------------
        # CẬP NHẬT LOGIC THEO TRẠNG THÁI
        # ----------------------------------------------------------------------
        if current_state == STATE_GAME:
            game.update_dice_phase()

        # ----------------------------------------------------------------------
        # BẮT SỰ KIỆN CHUỘT & BÀN PHÍM (EVENT HANDLING CHUẨN)
        # ----------------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 1. Sự kiện tại màn hình MENU
                if current_state == STATE_MENU:
                    play_sfx(sound_button2)
                    if 360 < mx < 650 and 490 < my < 550:
                        # Bắt đầu ván mới
                        game.reset()
                        pygame.mixer.music.stop()
                        current_state = STATE_GAME
                    elif 360 < mx < 650 and 560 < my < 620:
                        # Xem hướng dẫn
                        current_state = STATE_INSTRUCTION
                    elif 360 < mx < 650 and 630 < my < 690:
                        # Thoát trò chơi
                        running = False

                # 2. Sự kiện tại màn hình HƯỚNG DẪN
                elif current_state == STATE_INSTRUCTION:
                    if 660 < mx < 920 and 640 < my < 690:
                        play_sfx(sound_button2)
                        current_state = STATE_MENU

                # 3. Sự kiện tại màn hình CHƠI GAME
                elif current_state == STATE_GAME:
                    # Bấm nút End Game
                    if 705 < mx < 1000 and 720 < my < 770:
                        play_sfx(sound_button1)
                        play_music("BOOYAH_FINAL.wav", -1)
                        current_state = STATE_GAME_OVER

                    # Bấm nút Đổ xúc xắc
                    elif (705 < mx < 985) and (465 < my < 680):
                        if game.phase == PHASE_ROLL_DICE:
                            play_sfx(sound_button1)
                            game.roll_dice()

                    # Bấm chọn quân cờ sau khi đã đổ xúc xắc
                    elif game.phase == PHASE_SELECT_PIECE:
                        clicked_idx = get_clicked_seahorse(game.turn, mx, my, game.seahorses)
                        if clicked_idx != -1:
                            play_sfx(sound_button1)
                            game.move_piece(clicked_idx)

                # 4. Sự kiện tại màn hình KẾT THÚC (Click chuột để quay lại Menu)
                elif current_state == STATE_GAME_OVER:
                    play_sfx(sound_button2)
                    play_music("Pickleball.wav", -1)
                    current_state = STATE_MENU

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_state in (STATE_INSTRUCTION, STATE_GAME_OVER):
                        play_music("Pickleball.wav", -1)
                        current_state = STATE_MENU
                    elif current_state == STATE_GAME:
                        play_music("Pickleball.wav", -1)
                        current_state = STATE_MENU

        # ----------------------------------------------------------------------
        # RENDER GIAO DIỆN THEO TRẠNG THÁI HIỆN TẠI
        # ----------------------------------------------------------------------
        if current_state == STATE_MENU:
            draw_menu(screen, mx, my)
        elif current_state == STATE_INSTRUCTION:
            draw_instruction(screen, mx, my)
        elif current_state == STATE_GAME:
            draw_game(screen, mx, my, game)
        elif current_state == STATE_GAME_OVER:
            draw_game_over(screen, game)

        # Cập nhật màn hình duy nhất 1 lần mỗi frame
        pygame.display.flip()

        # Khóa tốc độ 60 FPS để CPU không bị quá tải
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()