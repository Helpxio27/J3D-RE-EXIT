# game/ui/theme.py
THEME = {
    "background":   (10, 10, 10),
    "primary":      (255, 255, 255),
    "accent":       (255, 220, 0),
    "danger":       (255, 60, 60),

    "font_title":   ("Arial", 72, True),   # name, size, bold
    "font_ui":      ("Arial", 40, False),
    "font_small":   ("Arial", 24, False),

    "button_color":         (30, 30, 30),
    "button_hover":         (50, 50, 50),
    "button_selected":      (255, 220, 0),
    "button_text":          (255, 255, 255),
    "button_text_selected": (0, 0, 0),
    "button_radius":        8,
    "button_padding":       (40, 16),      # x, y padding

    "anim_speed":   0.15,                  # lerp speed for transitions
    "shake_decay":  0.85,                  # how fast shake fades
}