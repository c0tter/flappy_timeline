import os, sys, random
import pygame
from textwrap import wrap

# ----------------------------------------------
# Flappy — Feature Timeline (Sprite + Background)
# ----------------------------------------------
# Folders (local):
#   ./assets/images/background-day.png
#   ./assets/images/bird.png
#   ./assets/fonts/*.ttf      (optional; auto-detected)
#   ./text/textN_top.txt
#   ./text/textN_bottom.txt
#
# Controls: Space/Click = flap, R = restart, L = reload text, Esc = quit
# ----------------------------------------------

# --- Layout ---
WIDTH, HEIGHT = 360, 640
GROUND_H = 90
PIPE_W = 170
GAP_H = 200
PIPE_SPACING = 280
START_X = 80

# Ensure text space even with short pipes
MIN_TOP_TEXT_H = 72
MIN_BOTTOM_TEXT_H = 96

# --- Physics ---
GRAVITY = 900.0
FLAP_V = -300.0
SCROLL_V = 130.0
FPS = 60

# --- Paths ---
BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
FONTS_DIR  = os.path.join(ASSETS_DIR, "fonts")
TEXT_DIR   = os.path.join(BASE_DIR, "text")

# --- Background toggle ---
USE_BACKGROUND_IMAGE = True      # set False to use flat color
BG_COLOR = (20, 32, 45)

# --- Bird sprite settings ---
BIRD_IMG_NAME   = "bird.png"     # file in assets/images/
BIRD_SCALE      = 0.7            # 0.5–1.0 usually good
BIRD_TILT       = True
BIRD_TILT_MIN   = -25            # degrees up
BIRD_TILT_MAX   =  60            # degrees down
BIRD_COLLISION_R = 14            # matches typical 32–48px sprite

# --- Font auto-detect ---
def pick_fonts():
    try:
        files = [f for f in os.listdir(FONTS_DIR) if f.lower().endswith(".ttf")]
    except FileNotFoundError:
        files = []
    if files:
        def find_first(names):
            for n in files:
                ln = n.lower()
                if any(tag in ln for tag in names): return os.path.join(FONTS_DIR, n)
            return None
        heading = find_first(["inter-bold","extrabold","semibold","black"]) or os.path.join(FONTS_DIR, files[0])
        milestone = find_first(["inter-regular","regular","medium"]) or heading
        print("Using fonts:", os.path.basename(heading), "/", os.path.basename(milestone))
        return heading, milestone
    print("No .ttf in assets/fonts — using system default.")
    return None, None

FONT_HEADING_PATH, FONT_MILESTONE_PATH = pick_fonts()

# --- Typography ---
HEADING_SIZE_BASE = 28
MILESTONE_SIZE_BASE = 20
LINE_SPACING = 4
INNER_PAD = 4   # text padding inside pipe (0–6 looks best)

# --- Colors ---
PIPE_BODY   = (30, 98, 176)      # darker so white text pops
PIPE_BORDER = (18, 62, 116)
TEXT_HEADING   = (255, 255, 255)
TEXT_MILESTONE = (255, 255, 255)

# ---------- text utilities ----------
def load_text_pairs():
    pairs, n = [], 1
    while True:
        top = os.path.join(TEXT_DIR, f"text{n}_top.txt")
        bot = os.path.join(TEXT_DIR, f"text{n}_bottom.txt")
        if not (os.path.exists(top) and os.path.exists(bot)): break
        with open(top, "r", encoding="utf-8") as f: t = f.read().strip()
        with open(bot, "r", encoding="utf-8") as f: b = f.read().strip()
        t = t.upper()
        b = (b[:1].upper() + b[1:]) if b else b
        pairs.append((t, b)); n += 1
    if not pairs:
        pairs = [("WELCOME", "Drop text files into /text and press L to reload.")]
    return pairs

def make_pipe_pair(offset_x, idx, text_pairs):
    safe_top = max(50, MIN_TOP_TEXT_H)
    safe_bottom = HEIGHT - GROUND_H - max(50, MIN_BOTTOM_TEXT_H)
    low  = safe_top + GAP_H / 2
    high = safe_bottom - GAP_H / 2
    gap_y = (safe_top + safe_bottom) / 2.0 if high <= low else random.uniform(low, high)
    heading, sub = text_pairs[idx % len(text_pairs)]
    return {"x": offset_x, "gap_y": gap_y, "passed": False, "idx": idx,
            "heading": heading, "subheading": sub}

# ---------- font/render ----------
def ensure_font(path, size, bold=False):
    try:
        if path: return pygame.font.Font(path, size)
    except Exception:
        pass
    f = pygame.font.Font(None, size)
    try: f.set_bold(bold)
    except Exception: pass
    return f

def render_wrapped_lines(text, font, max_width, max_lines=None):
    avg_w = max(1, font.size('M')[0])
    max_chars = max(1, int(max_width // avg_w))
    lines = []
    for para in (text or "").split('\n'):
        wrapped = wrap(para, max_chars, break_long_words=False, replace_whitespace=False)
        lines.extend(wrapped if wrapped else [""])
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        if lines: lines[-1] = lines[-1].rstrip() + "…"
    return lines

def render_lines_surface(lines, font, color, line_spacing=LINE_SPACING, align="center"):
    rendered = [font.render(line, True, color) for line in lines]
    w = max((s.get_width() for s in rendered), default=1)
    h = sum(s.get_height() for s in rendered) + (len(rendered)-1)*line_spacing
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    y = 0
    for s in rendered:
        x = (w - s.get_width()) // 2 if align == "center" else (w - s.get_width() if align == "right" else 0)
        surf.blit(s, (x, y))
        y += s.get_height() + line_spacing
    return surf

def fit_block(text, font_path, base_size, target_rect, color, bold=False, max_lines=None):
    max_w = max(1, target_rect.width  - 2*INNER_PAD)
    max_h = max(1, target_rect.height - 2*INNER_PAD)
    size, min_size = base_size, 10

    def render_try(txt, f):
        lines = render_wrapped_lines(txt, f, max_w, max_lines=max_lines)
        return render_lines_surface(lines, f, color, align="center")

    while size >= min_size:
        f = ensure_font(font_path, size, bold=bold)
        surf = render_try(text, f)
        if surf.get_width() <= max_w and surf.get_height() <= max_h:
            return surf
        size -= 1

    f = ensure_font(font_path, min_size, bold=bold)
    words = (text or "").split()
    if not words: return render_try("", f)
    while words:
        candidate = " ".join(words) + "…"
        surf = render_try(candidate, f)
        if surf.get_width() <= max_w and surf.get_height() <= max_h:
            return surf
        words.pop()
    return render_try("…", f)

def blit_outline_shadow(screen, surf, cx, cy):
    """
    Glyph-only shadow/outline via mask: no background rectangles.
    """
    x = int(cx - surf.get_width() // 2)
    y = int(cy - surf.get_height() // 2)
    mask = pygame.mask.from_surface(surf)

    # soft shadow
    shadow = mask.to_surface(setcolor=(0,0,0,110), unsetcolor=(0,0,0,0)).convert_alpha()
    screen.blit(shadow, (x+1, y+1))

    # 1px black outline
    outline_src = mask.to_surface(setcolor=(0,0,0,255), unsetcolor=(0,0,0,0)).convert_alpha()
    for ox, oy in [(-1,0),(1,0),(0,-1),(0,1)]:
        screen.blit(outline_src, (x+ox, y+oy))

    screen.blit(surf, (x, y))

# ---------- game ----------
class Game:
    def __init__(self):
        pygame.init(); pygame.font.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption("Flappy — Feature Timeline")
        self.clock = pygame.time.Clock()

        # Background
        self.bg_img = None
        if USE_BACKGROUND_IMAGE:
            bg_path = os.path.join(IMAGES_DIR, "background-day.png")
            if os.path.exists(bg_path):
                try:
                    self.bg_img = pygame.image.load(bg_path).convert()
                    self.bg_img = pygame.transform.smoothscale(self.bg_img, (WIDTH, HEIGHT))
                except Exception:
                    self.bg_img = None

        # Bird
        self.bird_img = None
        bird_path = os.path.join(IMAGES_DIR, BIRD_IMG_NAME)
        if os.path.exists(bird_path):
            try:
                img = pygame.image.load(bird_path).convert_alpha()
                if BIRD_SCALE != 1.0:
                    w, h = img.get_width(), img.get_height()
                    img = pygame.transform.smoothscale(img, (int(w*BIRD_SCALE), int(h*BIRD_SCALE)))
                self.bird_img = img
            except Exception:
                self.bird_img = None

        self.text_pairs = load_text_pairs()
        self.reset()

    def reset(self):
        self.bird_y = HEIGHT / 2
        self.vel_y = 0.0
        self.score = 0
        self.running = False
        self.game_over = False
        self.pipes = [
            make_pipe_pair(WIDTH + 90, 0, self.text_pairs),
            make_pipe_pair(WIDTH + 90 + PIPE_SPACING, 1, self.text_pairs),
            make_pipe_pair(WIDTH + 90 + PIPE_SPACING*2, 2, self.text_pairs),
        ]
        self.ground_phase = 0.0

    def reload_texts(self):
        self.text_pairs = load_text_pairs()
        for p in self.pipes:
            h, s = self.text_pairs[p["idx"] % len(self.text_pairs)]
            p["heading"], p["subheading"] = h, s

    def flap(self):
        if not self.running: self.running = True
        if self.game_over: return
        self.vel_y = FLAP_V

    def end_game(self):
        if not self.game_over:
            self.game_over = True
            self.running = False

    def update(self, dt):
        if self.running and not self.game_over:
            self.vel_y += GRAVITY * dt
            self.bird_y += (self.vel_y + GRAVITY * dt * 0.5) * dt

            new_pipes = []
            rightmost = max(p["x"] for p in self.pipes)
            max_idx = max(p["idx"] for p in self.pipes)
            for p in self.pipes:
                p["x"] -= SCROLL_V * dt
                if p["x"] + PIPE_W < 0:
                    p = make_pipe_pair(rightmost + PIPE_SPACING, max_idx + 1, self.text_pairs)
                    rightmost = p["x"]; max_idx = p["idx"]
                if (not p["passed"]) and (p["x"] + PIPE_W / 2 < START_X):
                    p["passed"] = True; self.score += 1
                new_pipes.append(p)
            self.pipes = new_pipes

            # collisions (circle)
            r = BIRD_COLLISION_R
            b_top = self.bird_y - r
            b_bot = self.bird_y + r
            if b_top < 0 or b_bot > HEIGHT - GROUND_H:
                self.end_game()
            else:
                for p in self.pipes:
                    in_x = (START_X + r > p["x"]) and (START_X - r < p["x"] + PIPE_W)
                    if in_x:
                        gap_top = p["gap_y"] - GAP_H / 2
                        gap_bot = p["gap_y"] + GAP_H / 2
                        if b_top < gap_top or b_bot > gap_bot:
                            self.end_game(); break

            self.ground_phase = (self.ground_phase - SCROLL_V * dt) % 48

    # --- drawing ---
    def draw_pipes(self):
        for p in self.pipes:
            gap_top = int(p["gap_y"] - GAP_H / 2)
            gap_bot = int(p["gap_y"] + GAP_H / 2)

            top_rect = pygame.Rect(int(p["x"]), 0, PIPE_W, gap_top)
            bottom_rect = pygame.Rect(int(p["x"]), gap_bot, PIPE_W, HEIGHT - GROUND_H - gap_bot)

            if top_rect.height < MIN_TOP_TEXT_H:       top_rect.height = MIN_TOP_TEXT_H
            if bottom_rect.height < MIN_BOTTOM_TEXT_H: bottom_rect.height = MIN_BOTTOM_TEXT_H

            radius = 16
            pygame.draw.rect(self.screen, PIPE_BODY, top_rect,    border_radius=radius)
            pygame.draw.rect(self.screen, PIPE_BODY, bottom_rect, border_radius=radius)
            pygame.draw.rect(self.screen, PIPE_BORDER, top_rect,    width=3, border_radius=radius)
            pygame.draw.rect(self.screen, PIPE_BORDER, bottom_rect, width=3, border_radius=radius)

            head = fit_block(p.get("heading",""), FONT_HEADING_PATH, HEADING_SIZE_BASE,
                             top_rect, TEXT_HEADING, bold=True, max_lines=2)
            mile = fit_block(p.get("subheading",""), FONT_MILESTONE_PATH, MILESTONE_SIZE_BASE,
                             bottom_rect, TEXT_MILESTONE, bold=False, max_lines=4)

            blit_outline_shadow(self.screen, head, top_rect.centerx, top_rect.centery)
            blit_outline_shadow(self.screen, mile, bottom_rect.centerx, bottom_rect.centery)

    def draw_ground(self):
        y = HEIGHT - GROUND_H
        x = -self.ground_phase
        toggle = True
        while x < WIDTH + 48:
            color = (34,197,94) if toggle else (22,163,74)
            pygame.draw.rect(self.screen, color, (int(x), y, 48, GROUND_H))
            x += 48; toggle = not toggle

    def draw_bird(self):
        x, y = START_X, int(self.bird_y)
        if self.bird_img:
            img = self.bird_img
            if BIRD_TILT:
                # map velocity to tilt angle
                t = max(min(self.vel_y, 400.0), -400.0)
                angle = (t / 400.0) * BIRD_TILT_MAX
                if t < 0: angle = max(angle, BIRD_TILT_MIN)
                img = pygame.transform.rotozoom(self.bird_img, -angle, 1.0)
            rect = img.get_rect(center=(x, y))
            self.screen.blit(img, rect.topleft)
        else:
            # fallback circle
            pygame.draw.circle(self.screen, (255,205,0), (x,y), 16)
            pygame.draw.circle(self.screen, (230,180,0), (x,y), 16, 3)
            pygame.draw.circle(self.screen, (255,255,255), (x+6, y-6), 4)
            pygame.draw.circle(self.screen, (0,0,0), (x+7, y-6), 2)

    def draw_overlay(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,90)); self.screen.blit(overlay, (0,0))
        f_big = ensure_font(FONT_HEADING_PATH, 34, True)
        f_ui  = ensure_font(FONT_MILESTONE_PATH, 20, False)
        white = (255,255,255)
        if not self.running and not self.game_over:
            t1 = f_big.render("Feature Timeline", True, white)
            t2 = f_ui.render("Space/Click: flap · R: restart · L: reload text", True, white)
            self.screen.blit(t1, (WIDTH//2 - t1.get_width()//2, HEIGHT//2 - 70))
            self.screen.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2 - 30))
        else:
            t1 = f_big.render("Game Over", True, white)
            t2 = f_ui.render(f"For Boring Video", True, white)
            t3 = f_ui.render("Wed, Oct 1, 2025, ", True, white)
            self.screen.blit(t1, (WIDTH//2 - t1.get_width()//2, HEIGHT//2 - 70))
            self.screen.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2 - 30))
            self.screen.blit(t3, (WIDTH//2 - t3.get_width()//2, HEIGHT//2 + 10))

    def draw_background(self):
        if USE_BACKGROUND_IMAGE and self.bg_img:
            self.screen.blit(self.bg_img, (0,0))
        else:
            self.screen.fill(BG_COLOR)

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit(0)
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_UP): self.flap()
                    elif event.key == pygame.K_r: self.reset()
                    elif event.key == pygame.K_l: self.reload_texts()
                    elif event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit(0)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.flap()

            if self.running and not self.game_over:
                self.update(min(0.033, dt))
            else:
                self.ground_phase = (self.ground_phase - SCROLL_V * dt * 0.3) % 48

            self.draw_background()
            self.draw_pipes()
            self.draw_bird()
            self.draw_ground()
            if (not self.running) or self.game_over:
                self.draw_overlay()
            pygame.display.flip()

if __name__ == "__main__":
    Game().run()
