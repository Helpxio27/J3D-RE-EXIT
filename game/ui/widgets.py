# game/ui/widgets.py
import pygame
from game.ui.theme import THEME
from game.ui.animator import lerp, lerp_color

# =====================
# FONT CACHE
# Fonts are expensive to create — cache them
# =====================
_font_cache = {}

def get_font(font_key):
    """Returns a cached pygame font from a theme font key"""
    if font_key not in _font_cache:
        name, size, bold = THEME[font_key]
        _font_cache[font_key] = pygame.font.SysFont(name, size, bold=bold)
    return _font_cache[font_key]


# =====================
# LABEL
# Static or animated text
# =====================
class Label:
    def __init__(self, text, font_key="font_ui", color_key="primary", alpha=255):
        self.text = text
        self.font_key = font_key
        self.color_key = color_key
        self.alpha = alpha          # current alpha
        self.target_alpha = alpha   # what we're animating toward

    def fade_in(self):
        self.alpha = 0
        self.target_alpha = 255

    def fade_out(self):
        self.target_alpha = 0

    def update(self):
        self.alpha = lerp(self.alpha, self.target_alpha, THEME["lerp_speed"])

    def draw(self, screen, x, y, anchor="topleft"):
        font = get_font(self.font_key)
        color = THEME[self.color_key]
        surf = font.render(self.text, True, color)
        surf.set_alpha(int(self.alpha))
        rect = surf.get_rect()
        setattr(rect, anchor, (x, y))
        screen.blit(surf, rect)


# =====================
# BUTTON
# Handles hover, selection, click — designer sets style via theme
# =====================
class Button:
    def __init__(self, text, font_key="font_ui", style="default"):
        self.text = text
        self.font_key = font_key
        self.style = style          # "default", "selected", "danger"

        # Animation state
        self._anim_t = 0.0          # 0 = default, 1 = selected/hover
        self.alpha = 255
        self.target_alpha = 255

        # Slide-in animation
        self.offset_x = 0.0
        self.target_offset_x = 0.0

    @property
    def is_selected(self):
        return self.style == "selected"
    
    def set_selected(self, selected: bool):
        self.style = "selected" if selected else "default"

    def slide_in_from_left(self, distance=200):
        """Call this to animate the button sliding in"""
        self.offset_x = -distance
        self.target_offset_x = 0.0

    def fade_in(self):
        self.alpha = 0
        self.target_alpha = 255

    def update(self):
        # Animate selection state
        target_t = 1.0 if self.style == "selected" else 0.0
        self._anim_t = lerp(self._anim_t, target_t, THEME["lerp_speed_fast"])

        # Animate slide
        self.offset_x = lerp(self.offset_x, self.target_offset_x, THEME["lerp_speed"])

        # Animate alpha
        self.alpha = lerp(self.alpha, self.target_alpha, THEME["lerp_speed"])

    def draw(self, screen, x, y, anchor="midleft"):
        font = get_font(self.font_key)

        # Pick colors based on style + animation
        if self.style == "danger":
            bg_color  = THEME["btn_color_danger"]
            txt_color = THEME["btn_text_danger"]
        else:
            bg_color  = lerp_color(THEME["btn_color"], THEME["btn_color_selected"], self._anim_t)
            txt_color = lerp_color(THEME["btn_text"], THEME["btn_text_selected"], self._anim_t)

        text_surf = font.render(self.text, True, txt_color)
        pw = THEME["btn_padding_x"]
        ph = THEME["btn_padding_y"]
        btn_w = text_surf.get_width()  + pw * 2
        btn_h = text_surf.get_height() + ph * 2

        # Build button surface
        btn_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)

        # Background
        pygame.draw.rect(btn_surf, (*bg_color, int(self.alpha)),
                         (0, 0, btn_w, btn_h),
                         border_radius=THEME["btn_radius"])

        # Border
        border_color = lerp_color(THEME["border"], THEME["accent"], self._anim_t)
        pygame.draw.rect(btn_surf, (*border_color, int(self.alpha)),
                         (0, 0, btn_w, btn_h),
                         width=THEME["btn_border_width"],
                         border_radius=THEME["btn_radius"])

        # Text
        text_surf.set_alpha(int(self.alpha))
        btn_surf.blit(text_surf, (pw, ph))

        # Apply slide offset
        draw_x = x + int(self.offset_x)
        rect = btn_surf.get_rect()
        setattr(rect, anchor, (draw_x, y)) 
        screen.blit(btn_surf, rect) 
        
        return rect  # return rect so caller can do hit testing if needed


# =====================
# LOGO
# Animated title with accent color on last word
# =====================
class Logo:
    def __init__(self):
        self.alpha = 0
        self.target_alpha = 255
        self.offset_y = 40.0
        self.target_offset_y = 0.0

    def animate_in(self):
        self.alpha = 0
        self.target_alpha = 255
        self.offset_y = 40.0
        self.target_offset_y = 0.0

    def update(self):
        self.alpha = lerp(self.alpha, self.target_alpha, THEME["lerp_speed"])
        self.offset_y = lerp(self.offset_y, self.target_offset_y, THEME["lerp_speed"])

    def draw(self, screen, x, y, anchor="midtop"):
        font = get_font("logo_font")
        text = THEME["logo_text"]

        # Split last word to color it as accent
        words = text.split(" ")
        if len(words) > 1:
            main_text   = " ".join(words[:-1]) + " "
            accent_text = words[-1]
        else:
            main_text   = ""
            accent_text = text

        main_surf   = font.render(main_text,   True, THEME["logo_color"])
        accent_surf = font.render(accent_text, True, THEME["logo_accent_color"])

        total_w = main_surf.get_width() + accent_surf.get_width()
        total_h = max(main_surf.get_height(), accent_surf.get_height())

        combined = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
        combined.blit(main_surf,   (0, 0))
        combined.blit(accent_surf, (main_surf.get_width(), 0))
        combined.set_alpha(int(self.alpha))

        draw_y = y + int(self.offset_y)
        rect = combined.get_rect()
        setattr(rect, anchor, (x, draw_y))
        screen.blit(combined, rect)


# =====================
# LOADING BAR
# =====================
class LoadingBar:
    def __init__(self, width, height=None):
        self.width = width
        self.height = height or THEME["loading_bar_height"]
        self.progress = 0.0        # 0.0 to 1.0
        self.visual_progress = 0.0 # animated version

    def set_progress(self, value):
        self.progress = max(0.0, min(1.0, value))

    def update(self):
        self.visual_progress = lerp(
            self.visual_progress,
            self.progress,
            THEME["lerp_speed_fast"]
        )

    def draw(self, screen, x, y, anchor="midtop"):
        r = THEME["loading_bar_radius"]

        bg_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, THEME["loading_bar_bg"],
                         (0, 0, self.width, self.height),
                         border_radius=r)

        fill_w = int(self.width * self.visual_progress)
        if fill_w > 0:
            pygame.draw.rect(bg_surf, THEME["loading_bar_color"],
                             (0, 0, fill_w, self.height),
                             border_radius=r)

        rect = bg_surf.get_rect()
        setattr(rect, anchor, (x, y))
        screen.blit(bg_surf, rect)