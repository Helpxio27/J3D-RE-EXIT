# game/ui/theme.py

THEME = {
    # =====================
    # COLORS
    # =====================
    "background":           (10, 10, 10),
    "surface":              (20, 20, 20),      # cards, panels
    "surface_hover":        (35, 35, 35),
    "border":               (60, 60, 60),

    "primary":              (255, 255, 255),   # main text
    "secondary":            (140, 140, 140),   # subtitles, hints
    "accent":               (255, 220, 0),     # selected, highlights
    "danger":               (255, 60, 60),     # exit, warnings
    "success":              (60, 220, 100),    # confirmations

    # =====================
    # TYPOGRAPHY
    # =====================
    "font_title":           ("Arial", 72, True),
    "font_subtitle":        ("Arial", 32, False),
    "font_ui":              ("Arial", 40, False),
    "font_small":           ("Arial", 24, False),
    "font_timer":           ("Arial", 28, True),

    # =====================
    # BUTTONS
    # =====================
    "btn_padding_x":        48,
    "btn_padding_y":        18,
    "btn_radius":           10,
    "btn_border_width":     2,

    "btn_color":            (20, 20, 20),
    "btn_color_hover":      (35, 35, 35),
    "btn_color_selected":   (255, 220, 0),
    "btn_color_danger":     (255, 60, 60),

    "btn_text":             (255, 255, 255),
    "btn_text_selected":    (0, 0, 0),
    "btn_text_danger":      (255, 255, 255),

    # =====================
    # ANIMATIONS
    # =====================
    "lerp_speed":           0.15,     # general smoothing speed
    "lerp_speed_slow":      0.06,     # slow transitions
    "lerp_speed_fast":      0.30,     # snappy transitions

    # =====================
    # LOGO
    # =====================
    "logo_text":            "RE-EXIT",
    "logo_font":            ("Arial", 96, True),
    "logo_color":           (255, 255, 255),
    "logo_accent_color":    (255, 220, 0),

    # =====================
    # LOADING SCREEN
    # =====================
    "loading_bar_color":    (255, 220, 0),
    "loading_bar_bg":       (40, 40, 40),
    "loading_bar_height":   8,
    "loading_bar_radius":   4,
}